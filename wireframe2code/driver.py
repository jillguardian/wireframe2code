import argparse

import cv2
import imutils

import paper
import segment


def show_image(title, image):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyWindow(title)


def main(args):
    if args.use_camera and args.filename is not None:
        raise Exception("Camera and image cannot be simultaneously provided")
    if args.use_camera:
        capture = cv2.VideoCapture(0)
        while True:
            can_read, frame = capture.read()
            if can_read:
                process(frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break
        capture.release()
        cv2.destroyAllWindows()
    elif args.filename is not None:
        image = cv2.imread(args.filename)
        process(image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        raise Exception("Must provide arguments")

    cv2.destroyAllWindows()


def process(image):
    # Image has to be resized for better approximation and performance
    image = imutils.resize(image, width=500)

    capture = paper.Capture(image)
    contours = capture.contours(predicate=lambda contour: cv2.arcLength(contour, True) >= 100)

    for contour in contours:
        if segment.is_square(contour):
            cv2.drawContours(image, [contour], -1, (255, 0, 0), 2)
        cv2.imshow("Squares", image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", dest="filename", help="Path to input image")
    parser.add_argument("-c", "--camera", dest="use_camera", help="Flag for using camera as source",
                        action='store_true')
    parsed_args, unparsed_args = parser.parse_known_args()
    main(parsed_args)
