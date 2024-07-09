import argparse
from tflite_model_maker import image_classifier
from tflite_model_maker.image_classifier import DataLoader


def main(output_filename: str, image_files: list[str]):
    data = DataLoader.from_folder("flower_photos/")
    model = image_classifier.create(data)
    loss, accuracy = model.evaluate()
    model.export(export_dir=f"./models/{output_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a model.")
    parser.add_argument(
        "output_filename",
        type=str,
        help="The filename of the model to output.",
    )
    parser.add_argument(
        "image_files",
        type=str,
        nargs="+",
        help="The directories that contains image files to use for training.",
    )

    parsed_args = parser.parse_args()

    output_filename: str = parsed_args.output_filename
    image_files: list[str] = parsed_args.image_files

    main(output_filename, image_files)
