import imutils
import numpy as np
from cv2 import cv2
from cv2 import ximgproc


class Capture:

    def __init__(self,
                 image,
                 transform=lambda image: image if image.shape[0] <= 640 else imutils.resize(image, width=640)):
        # TODO: Determine where to resize image
        # TODO: Determine optimal image size for better approximation and performance
        self.image = transform(image)

    def preprocess(self):
        block_size = 40
        delta = 25

        gamma_corrected = Capture.__adjust_gamma(self.image)
        adaptively_binarized = Capture.__adaptively_binarize(gamma_corrected, block_size, delta)
        softened_binarization = Capture.__soften_binarization(self.image, adaptively_binarized, block_size)
        inversed = cv2.threshold(softened_binarization, 127, 255, cv2.THRESH_BINARY_INV)[1]
        dilated = cv2.dilate(inversed, kernel=None, iterations=1)
        thinned = ximgproc.thinning(dilated, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)

        return [gamma_corrected, adaptively_binarized, softened_binarization, inversed, dilated, thinned]

    @staticmethod
    def __adjust_gamma(image, gamma=1.2):
        # Build a lookup table mapping the pixel values [0, 255] to their adjusted gamma values
        inverse_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inverse_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        # Apply gamma correction using the lookup table
        return cv2.LUT(image, table)

    @staticmethod
    def __adaptively_binarize(image, block_size, delta):
        def preprocess(image):
            """
            Do necessary noise cleaning.
            """
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = cv2.medianBlur(image, 3)
            return 255 - image

        def postprocess(image):
            kernel = np.ones((3, 3), np.uint8)
            image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
            return image

        def apply_adaptive_median_thresholding(image_slice, delta):
            """
            Perform binarization from the median value locally. The following assumptions are held:
            - The majority of pixels in the slice is background.
            - The median value of the intensity histogram probably belongs to the background.
            We allow a soft margin delta to account for any irregularities.
            - We need to keep everything other than the background.
            """
            median = np.median(image_slice)
            output = np.zeros_like(image_slice)
            output[image_slice - median < delta] = 255
            kernel = np.ones((3, 3), np.uint8)
            output = 255 - cv2.dilate(255 - output, kernel, iterations=2)
            return output

        def binarize_by_block(image, block_size, delta):
            """
            Divides the provided image into local regions (blocks), and applies binarization to each block.
            """
            output = np.zeros_like(image)
            for row in range(0, image.shape[0], block_size):
                for col in range(0, image.shape[1], block_size):
                    index = (row, col)
                    index = Capture.__get_block_index(image.shape, index, block_size)
                    output[index] = apply_adaptive_median_thresholding(image[index], delta)
            return output

        preprocessed = preprocess(image)
        binarized = binarize_by_block(preprocessed, block_size, delta)
        postprocessed = postprocess(binarized)
        return postprocessed

    @staticmethod
    def __get_block_index(image_shape, yx, block_size):
        """
        Helper function that generates box coordinates.
        """
        y = np.arange(max(0, yx[0] - block_size), min(image_shape[0], yx[0] + block_size))
        x = np.arange(max(0, yx[1] - block_size), min(image_shape[1], yx[1] + block_size))
        return np.meshgrid(y, x)

    @staticmethod
    def __soften_binarization(image, mask, block_size):
        def sigmoid(x, orig, rad):
            k = np.exp((x - orig) * 5 / rad)
            return k / (k + 1.)

        def apply_sigmoid(img_in, mask):
            # First, we pre-fill the masked region of img_out to white (background).
            # The mask is retrieved from previous section.
            img_out = np.zeros_like(img_in)
            img_out[mask == 255] = 255
            fimg_in = img_in.astype(np.float32)

            # Then, we store the foreground (letters written with ink) in the `idx` array.
            # If there are none (i.e. just background), we move on to the next block.
            idx = np.where(mask == 0)
            if idx[0].shape[0] == 0:
                img_out[idx] = img_in[idx]
                return img_out

            # We find the intensity range of our pixels in this local part,
            # and clip the image block to that range locally.
            lo = fimg_in[idx].min()
            hi = fimg_in[idx].max()
            v = fimg_in[idx] - lo
            r = hi - lo

            # Now we use good old OTSU binarization to get a rough estimation
            # of foreground and background regions.
            img_in_idx = img_in[idx]
            ret3, th3 = cv2.threshold(img_in[idx], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Then we normalize and apply the Sigmoid function to gradually combine blocks.
            bound_value = np.min(img_in_idx[th3[:, 0] == 255])
            bound_value = (bound_value - lo) / (r + 1e-5)
            f = (v / (r + 1e-5))
            f = sigmoid(f, bound_value + 0.05, 0.2)

            # Finally, we re-normalize the result to the range [0..255].
            img_out[idx] = (255. * f).astype(np.uint8)
            return img_out

        def combine_blocks(image, mask, block_size):
            """
            Applies the combination routine on local blocks so that the scaling parameters of the Sigmoid function
            can be adjusted to the local setting.
            """
            output_image = np.zeros_like(image)
            for row in range(0, image.shape[0], block_size):
                for col in range(0, image.shape[1], block_size):
                    index = (row, col)
                    block_index = Capture.__get_block_index(image.shape, index, block_size)
                    output_image[block_index] = apply_sigmoid(image[block_index], mask[block_index])
            return output_image

        def preprocess(image):
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        def postprocess(image):
            # TODO
            return image

        preprocessed = preprocess(image)
        binarized = combine_blocks(preprocessed, mask, block_size)
        postprocessed = postprocess(binarized)
        return postprocessed

    def contours(self, predicate=lambda contour: True):
        image = self.preprocess()[-1]
        contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours[:] = [contour for contour in contours if predicate(contour)]
        return contours
