"""AidSorter - Automatic Goods Sorting System

This module contains the system that handles camera features.
"""

# quit your whining
# pyright: reportDeprecated=false

import time

import cv2

from aidsorter import detector, exceptions, info, visualizer
from aidsorter.fps_config import FPSConfig
from aidsorter.logger import LoggerFactory
from aidsorter.mcu import MCU
from aidsorter.mcu_config import MCUConfig


def getCameraCapture(camera_id: int, resolution: tuple[int, int]) -> cv2.VideoCapture:
    logger = LoggerFactory().get_logger(__name__)
    logger.info("Getting camera capture...")
    cam_cap = cv2.VideoCapture(camera_id)
    logger.info("Backend API name: %s", cam_cap.getBackendName())
    if not cam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0]):
        raise exceptions.CameraError("Unable to set the camera width.")

    if not cam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1]):
        raise exceptions.CameraError("Unable to set the camera height.")

    return cam_cap


def capture(
    config_path: str,
    camera_id: int = 1,
    *,
    mcu_port: str = "/dev/ttyUSB0",
    model_name: str = "default.tflite",
    camera_feed: bool = True,
) -> int:
    """Capture video from the camera and detect objects.

    Args:
        config_path: The path of the configuration file.
        camera_id: The ID of the camera to use. (default: 0)
        mcu_port: The port of the MCU. (default: "/dev/ttyUSB0")
        model_name: The name of the model to use. (default: "default.tflite")
        camera_feed: Display the camera feed. (default: True)

    Raises:
        exceptions.CameraError: Raised when the camera is not available.

    Returns:
        The exit code.
    """

    fps = FPSConfig()
    config = MCUConfig(config_path)
    stats_style = visualizer.StatsStyle()
    tf_detector = detector.create_detector(model_name, config.cpu_threads)
    mcu = MCU(mcu_port, config.baudrate, config.mcu_connection_timeout)
    object_sorting_in_progress: int = -1  # which bucket is targeted for the object
    object_category_samples: list[str] = []
    object_category_samples_expiration: int = 0

    logger = LoggerFactory().get_logger(__name__)
    logger.info("Starting the detection process...")
    logger.info("Using camera ID: %s", camera_id)
    logger.info(
        "Using camera resolution: %sx%s", config.resolution[0], config.resolution[1]
    )
    logger.info("Using CPU threads: %s", config.cpu_threads)
    cam_cap = getCameraCapture(camera_id, config.resolution)

    logger.info("Starting camera loop...")
    fps.start_time = time.time()  # Start the timer
    while cam_cap.isOpened():
        try:
            read_success, image = cam_cap.read()
            if not read_success:
                logger.error("Unable to read data from webcam.")
                raise exceptions.CameraError("ERROR: Unable to read data from webcam.")

            fps.frame_count += 1
            image = cv2.flip(image, 1)

            # Detect objects in the image
            detection_result = detector.detect_objects(tf_detector, image)
            logger.info("Detected objects: %d", len(detection_result.detections))
            # logger.debug("Raw Detection: %s", detection_result.detections)
            logger.debug(
                "Detection: %s",
                [
                    ",".join([dc.category_name for dc in detection.categories])
                    for detection in detection_result.detections
                ],
            )

            if object_sorting_in_progress != -1:
                # Here, we wait for the object to fall into the bucket.
                try:
                    if mcu.ir_states[object_sorting_in_progress - 1]:
                        mcu.set_gate_state(object_sorting_in_progress, False)
                        # just acknowledge all IR states...
                        # _ = mcu.acknowledge_ir_state(object_sorting_in_progress)
                        logger.debug("Acknowledging all IR states...")
                        for i in range(1, 6):
                            _ = mcu.acknowledge_ir_state(i)

                        logger.info(
                            "Nahulog na siya kay %s.", object_sorting_in_progress
                        )
                        object_sorting_in_progress = -1
                        mcu.platform_deactivate()
                        mcu.show_statistics()

                except IndexError:
                    logger.error("Unable to get IR statuses. Please check the MCU.")

                continue

            if len(detection_result.detections) > 1:
                object_category_samples_expiration = 0
                mcu.set_err_led(True)
                logger.error(
                    "%s object/s detected. Will not proceed.",
                    len(detection_result.detections),
                )

            elif len(detection_result.detections) == 1:
                object_category_samples_expiration = 0
                mcu.set_err_led(False)
                logger.debug(
                    "object_sorting_in_progress=%s", object_sorting_in_progress
                )

                object_category: str = (
                    detection_result.detections[0].categories[0].category_name
                )

                if (
                    len(object_category_samples) < config.detector_samples
                    and object_sorting_in_progress == -1
                ):
                    logger.debug("Taking sample #%s.", len(object_category_samples) + 1)
                    object_category_samples.append(object_category)
                    continue

                logger.debug("Samples: %s", object_category_samples)
                object_category = max(
                    set(object_category_samples), key=object_category_samples.count
                )
                logger.info(
                    "Object category from %s samples: %s (%s%%)",
                    config.detector_samples,
                    object_category,
                    object_category_samples.count(object_category)
                    / config.detector_samples
                    * 100,
                )
                object_category_samples.clear()

                # Here, we sort the object to the correct bucket.
                if object_category in config.bucket_contents[0]:
                    logger.info("Object %s belongs to Bucket 1.", object_category)
                    mcu.set_gate_state(1, True)
                    mcu.platform_activate()
                    object_sorting_in_progress = 1

                elif object_category in config.bucket_contents[1]:
                    logger.info("Object %s belongs to Bucket 2.", object_category)
                    mcu.set_gate_state(2, True)
                    mcu.platform_activate()
                    object_sorting_in_progress = 2

                elif object_category in config.bucket_contents[2]:
                    logger.info("Object %s belongs to Bucket 3.", object_category)
                    mcu.set_gate_state(3, True)
                    mcu.platform_activate()
                    object_sorting_in_progress = 3

                elif object_category in config.bucket_contents[3]:
                    logger.info("Object %s belongs to Bucket 4.", object_category)
                    mcu.set_gate_state(4, True)
                    mcu.platform_activate()
                    object_sorting_in_progress = 4

                else:
                    logger.warning("Unknown object category: %s", object_category)
                    logger.warning("Object will be put in Bucket 5.")
                    mcu.platform_activate()
                    object_sorting_in_progress = 5

                mcu.acknowledge_object_sort()

            elif len(detection_result.detections) == 0:
                if len(object_category_samples) != 0:
                    if object_category_samples_expiration < config.detector_samples:
                        object_category_samples_expiration += 1
                        continue

                    object_category_samples_expiration = 0
                    logger.info(
                        "No object detected after %s frames. Clearing %s samples.",
                        config.detector_samples,
                        len(object_category_samples),
                    )
                    object_category_samples.clear()

            # Calculate the FPS
            if fps.frame_count % fps.avg_frame_count == 0:
                fps.end_time = time.time()
                fps.latest_fps = fps.avg_frame_count / (fps.end_time - fps.start_time)
                fps.start_time = time.time()
                logger.debug("FPS = %s", fps.latest_fps)
                fps.add_record(fps.latest_fps)

            if camera_feed:
                # draw detection results,
                # draw FPS stats,
                # and display the camera feed.
                cv2.imshow(
                    f"{info.TITLE} | Camera Feed",
                    visualizer.draw_fps(
                        visualizer.draw_detection_result(
                            image, detection_result, stats_style
                        ),
                        fps.latest_fps,
                        (fps.minimum, fps.maximum, fps.average),
                        stats_style,
                    ),
                )

                # Stop the program if the ESC key is pressed.
                if cv2.waitKey(1) == 27:
                    logger.info("ESC key pressed. Exiting...")
                    break

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt detected.")
            break

        except exceptions.CameraError as e:
            logger.error("An error occurred: %s", e)
            logger.info("Restarting after %s seconds...", info.ERROR_RESTART_DELAY)
            mcu.set_err_led(True)
            time.sleep(info.ERROR_RESTART_DELAY)
            mcu.set_err_led(False)
            cam_cap = getCameraCapture(camera_id, config.resolution)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.critical("An error occurred: %s", e)
            logger.info("Restarting after %s seconds...", info.ERROR_RESTART_DELAY)
            mcu.set_err_led(True)
            time.sleep(info.ERROR_RESTART_DELAY)
            mcu.set_err_led(False)

    logger.info("Releasing camera...")
    cam_cap.release()
    logger.info("Destroying all windows...")
    cv2.destroyAllWindows()
    logger.info("Putting MCU on standby...")
    mcu.show_standby()
    logger.info("Done.")
    logger.info("Min FPS: %s", fps.minimum)
    logger.info("Max FPS: %s", fps.maximum)
    logger.info("Avg FPS: %s", fps.average)

    return 0
