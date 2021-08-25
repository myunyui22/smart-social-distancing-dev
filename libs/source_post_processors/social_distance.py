import logging 
import math 
import numpy as np 
import cv2 
  
from scipy.spatial.distance import cdist 
from libs.utils.camera_calibration import get_camera_calibration_path 
from tools.objects_post_process import extract_violating_objects 


logger = logging.getLogger(__name__) 

class SocialDistancePostProcessor: 

    # Distance methods 
    CALIBRATED_DISTANCE = "CalibratedDistance" 
    FOUR_CORNER_DISTANCE = "FourCornerPointsDistance" 
    CENTER_POINTS_DISTANCE = "CenterPointsDistance" 
    BIRD_VIEW_DISTANCE= "birdViewDistance" 

    def __init__(self, config, source: str, post_processor: str): 
        self.config = config 
        self.post_processor = self.config.get_section_dict(post_processor) 
        self.dist_threshold = float(self.post_processor["DistThreshold"]) 
        default_dist_method = self.post_processor["DefaultDistMethod"] 
        if self.config.get_section_dict(source).get("DistMethod"): 
            self.dist_method = self.config.get_section_dict(source).get("DistMethod") 
        else: 
            self.dist_method = default_dist_method 
        if self.dist_method == self.CALIBRATED_DISTANCE: 
            calibration_file = get_camera_calibration_path( 
                self.config, self.config.get_section_dict(source)["Id"]) 
            try: 
                with open(calibration_file, "r") as file: 
                    self.h_inv = file.readlines()[0].split(" ")[1:] 
                    self.h_inv = np.array(self.h_inv, dtype="float").reshape((3, 3)) 
            except FileNotFoundError: 
                logger.error("The specified 'CalibrationFile' does not exist") 
                logger.info(f"Falling back using {default_dist_method}") 
                self.dist_method = default_dist_method 
  
    def calculate_box_distances(self, nn_out): 
        """ 
        This function calculates a distance matrix for detected bounding boxes. 
        Three methods are implemented to calculate the distances, the first one estimates distance with a calibration matrix 
        which transform the points to the 3-d world coordinate, the second one estimates distance of center points of the 
        boxes and the third one uses minimum distance of each of 4 points of bounding boxes. 

        params: 
        object_list: a list of dictionaries. each dictionary has attributes of a detected object such as 
        "id", "centroidReal" (a tuple of the centroid coordinates (cx,cy,w,h) of the box) and "bboxReal" (a tuple 
        of the (xmin,ymin,xmax,ymax) coordinate of the box) 

        returns: 
        distances: a NxN ndarray which i,j element is estimated distance between i-th and j-th bounding box in real scene (cm) 
        """ 
        if self.dist_method == self.CALIBRATED_DISTANCE: 
            return self.calculate_calibrated_distance(nn_out) 
        elif self.dist_method == self.FOUR_CORNER_DISTANCE: 
            return self.calculate_four_corner_distance(nn_out) 
        elif self.dist_method == self.CENTER_POINTS_DISTANCE: 
            return self.calculate_center_points_distance(nn_out) 
        elif self.dist_method == self.BIRD_VIEW_DISTANCE: 
            return self.calculate_bird_view_distancing(nn_out) 
        else: 
            raise ValueError(f"Not supported distance method {self.dist_method}") 

    def calculate_four_corner_distance(self, nn_out): 
        distances = [] 
        for i in range(len(nn_out)): 
            distance_row = [] 
            for j in range(len(nn_out)): 
                if i == j: 
                    distance_row.append(0) 
                    continue 
                lower_left_of_first_box = [nn_out[i]["bboxReal"][0], nn_out[i]["bboxReal"][1], 
                                           nn_out[i]["centroidReal"][3]] 
                lower_right_of_first_box = [nn_out[i]["bboxReal"][2], nn_out[i]["bboxReal"][1], 
                                            nn_out[i]["centroidReal"][3]] 
                upper_left_of_first_box = [nn_out[i]["bboxReal"][0], nn_out[i]["bboxReal"][3], 
                                           nn_out[i]["centroidReal"][3]] 
                upper_right_of_first_box = [nn_out[i]["bboxReal"][2], nn_out[i]["bboxReal"][3], 
                                            nn_out[i]["centroidReal"][3]] 

                lower_left_of_second_box = [nn_out[j]["bboxReal"][0], nn_out[j]["bboxReal"][1], 
                                            nn_out[j]["centroidReal"][3]] 
                lower_right_of_second_box = [nn_out[j]["bboxReal"][2], nn_out[j]["bboxReal"][1], 
                                             nn_out[j]["centroidReal"][3]] 
                upper_left_of_second_box = [nn_out[j]["bboxReal"][0], nn_out[j]["bboxReal"][3], 
                                            nn_out[j]["centroidReal"][3]] 
                upper_right_of_second_box = [nn_out[j]["bboxReal"][2], nn_out[j]["bboxReal"][3], 
                                             nn_out[j]["centroidReal"][3]] 

                l1 = self.calculate_distance_of_two_points_of_boxes(nn_out, 
                    lower_left_of_first_box, lower_left_of_second_box) 
                l2 = self.calculate_distance_of_two_points_of_boxes(nn_out, 
                    lower_right_of_first_box, lower_right_of_second_box) 
                l3 = self.calculate_distance_of_two_points_of_boxes(nn_out, 
                    upper_left_of_first_box, upper_left_of_second_box) 
                l4 = self.calculate_distance_of_two_points_of_boxes(nn_out, 
                    upper_right_of_first_box, upper_right_of_second_box) 
                distance_row.append(min(l1, l2, l3, l4)) 
            distances.append(distance_row) 
        return np.asarray(distances, dtype=np.float32) 

    def calculate_center_points_distance(self, nn_out): 
        distances = [] 
        for i in range(len(nn_out)): 
            distance_row = [] 
            for j in range(len(nn_out)): 
                if i == j: 
                    distance_row.append(0) 
                    continue 
                center_of_first_box = [nn_out[i]["centroidReal"][0], nn_out[i]["centroidReal"][1], nn_out[i]["centroidReal"][3]] 
                center_of_second_box = [nn_out[j]["centroidReal"][0], nn_out[j]["centroidReal"][1], nn_out[j]["centroidReal"][3]] 
                distance_row.append(self.calculate_distance_of_two_points_of_boxes(nn_out, center_of_first_box, center_of_second_box)) 
            distances.append(distance_row) 
        return np.asarray(distances, dtype=np.float32) 

    def calculate_calibrated_distance(self, nn_out): 
        world_coordinate_points = np.array([self.transform_to_world_coordinate(bbox) for bbox in nn_out]) 
        if len(world_coordinate_points) == 0: 
            return np.array([]) 
        return cdist(world_coordinate_points, world_coordinate_points) 

    def calculate_bird_view_distancing(self, nn_out): 
        width = 750 
        height = 1000 

        corner_points = [[96, 398], [413,197], [656,602],[996,360]] 
        matrix_first_box = self.compute_perspective_transform(corner_points,width,height) 
        matrix_second_box = self.compute_perspective_transform(corner_points,width,height) 

        distances = [] 
        for i in range(len(nn_out)): 
            distance_row = [] 
            for j in range(len(nn_out)): 
                if i == j: 
                    distance_row.append(0) 
                    continue 
                lower_left_of_first_box = [nn_out[i]["bboxReal"][0], nn_out[i]["bboxReal"][1]] 
                lower_right_of_first_box = [nn_out[i]["bboxReal"][2], nn_out[i]["bboxReal"][1]] 
                upper_left_of_first_box = [nn_out[i]["bboxReal"][0], nn_out[i]["bboxReal"][3]] 
                upper_right_of_first_box = [nn_out[i]["bboxReal"][2], nn_out[i]["bboxReal"][3]] 
                first_box_center_array = [lower_left_of_first_box,lower_right_of_first_box,upper_left_of_first_box ,upper_right_of_first_box] 

                lower_left_of_second_box = [nn_out[j]["bboxReal"][0], nn_out[j]["bboxReal"][1]] 
                lower_right_of_second_box = [nn_out[j]["bboxReal"][2], nn_out[j]["bboxReal"][1]] 
                upper_left_of_second_box = [nn_out[j]["bboxReal"][0], nn_out[j]["bboxReal"][3]] 
                upper_right_of_second_box = [nn_out[j]["bboxReal"][2], nn_out[j]["bboxReal"][3]] 
                seconde_box_center_array = [lower_left_of_second_box,lower_right_of_second_box,upper_left_of_second_box,upper_right_of_second_box] 

                #logger.info('first_box_center_array : {}'.format(first_box_center_array)) 
                transformed_downoids_first_box = self.compute_point_perspective_transformation(matrix_first_box,first_box_center_array) 
                transformed_downoids_second_box = self.compute_point_perspective_transformation(matrix_second_box,seconde_box_center_array) 

                [fst_c1, fst_c2, fst_c3, fst_c4] = transformed_downoids_first_box 
                [scd_c1, scd_c2, scd_c3, scd_c4] = transformed_downoids_second_box 

                distance_between_two_boxes = [] 
                for k in range(4): 
                    [xc1, yc1] = transformed_downoids_first_box[k] 
                    [xc2, yc2] = transformed_downoids_second_box[k] 

                    dx = xc2 - xc1 
                    dy = yc2 - yc1 

                    distance_between_two_boxes.append(math.sqrt(dx**2 + dy**2)) 

                distance_row.append(min(distance_between_two_boxes)) 
            distances.append(distance_row) 
        return np.asarray(distances, dtype=np.float32) 

    def transform_to_world_coordinate(self, bbox): 
        """ 
        This function will transform the center of the bottom line of a bounding box from image coordinate to world 
        coordinate via a homography matrix 
        Args: 
            bbox: a dictionary of a  coordinates of a detected instance with "id", 
            "centroidReal" (a tuple of the centroid coordinates (cx,cy,w,h) of the box) and "bboxReal" (a tuple 
            of the (xmin,ymin,xmax,ymax) coordinate of the box) keys 

        Returns: 
            A numpy array of (X,Y) of transformed point 
        """ 

        floor_point = np.array([int((bbox["bboxReal"][0] + bbox["bboxReal"][2]) / 2), bbox["bboxReal"][3], 1]) 
        floor_world_point = np.matmul(self.h_inv, floor_point) 
        floor_world_point = floor_world_point[:-1] / floor_world_point[-1] 
        return floor_world_point 

    def calculate_distance_of_two_points_of_boxes(self, nn_out, first_point, second_point): 
        """ 
        This function calculates a distance l for two input corresponding points of two detected bounding boxes. 
        it is assumed that each person is H = 170 cm tall in real scene to map the distances in the image (in pixels) to 
        physical distance measures (in meters). 

        params: 
        first_point: (x, y, h)-tuple, where x,y is the location of a point (center or each of 4 corners of a bounding box) 
        and h is the height of the bounding box. 
        second_point: same tuple as first_point for the corresponding point of other box 

        returns: 
        l:  Estimated physical distance (in centimeters) between first_point and second_point. 
        """ 

        # estimate corresponding points distance 
         
        [xc1, yc1, h1] = first_point 
        [xc2, yc2, h2] = second_point 
        dx = xc2 - xc1 
        dy = yc2 - yc1 

        lx = dx * 170 * (1 / h1 + 1 / h2) / 2 
        ly = dy * 170 * (1 / h1 + 1 / h2) / 2 

        return math.sqrt(dx**2 + dy**2) 

    def compute_perspective_transform(self,corner_points,width,height): 
        """ Compute the transformation matrix 
        @ corner_points : 4 corner points selected from the image 
        @ height, width : size of the image 
        """ 
        # Create an array out of the 4 corner points 
        corner_points_array = np.float32(corner_points) 
        # Create an array with the parameters (the dimensions) required to build the matrix 
        img_params = np.float32([[0,0],[width,0],[0,height],[width,height]]) 
        # Compute and return the transformation matrix 
        matrix = cv2.getPerspectiveTransform(corner_points_array,img_params)  
        return matrix 

    def compute_point_perspective_transformation(self,matrix,list_downoids): 
        """ Apply the perspective transformation to every ground point which have been detected on the main frame. 
        @ matrix : the 3x3 matrix  
        @ list_downoids : list that contains the points to transform 
        return : list containing all the new points 
        """ 

        # Compute the new coordinates of our points 
        list_points_to_detect = np.float32(list_downoids).reshape(-1, 1, 2) 
        transformed_points = cv2.perspectiveTransform(list_points_to_detect, matrix) 
        # Loop over the points and add them to the list that will be returned 
        transformed_points_list = list() 
        for i in range(0,transformed_points.shape[0]): 
            transformed_points_list.append([transformed_points[i][0][0],transformed_points[i][0][1]]) 
        return transformed_points_list 

    def calculate_distancing(self, objects_list): 
        """ 
        this function post-process the raw boxes of object detector and calculate a distance matrix 
        for detected bounding boxes. 
        post processing is consist of: 
        1. omitting large boxes by filtering boxes which are bigger than the 1/4 of the size the image. 
        2. omitting duplicated boxes by applying an auxilary non-maximum-suppression. 
        3. apply a simple object tracker to make the detection more robust. 

        params: 
        object_list: a list of dictionaries. each dictionary has attributes of a detected object such as 
        "id", "centroid" (a tuple of the normalized centroid coordinates (cx,cy,w,h) of the box) and "bbox" (a tuple 
        of the normalized (xmin,ymin,xmax,ymax) coordinate of the box) 

        returns: 
        object_list: the post processed version of the input 
        distances: a NxN ndarray which i,j element is distance between i-th and l-th bounding box 
        """ 

        for i, item in enumerate(objects_list): 
            item["id"] = item["id"].split("-")[0] + "-" + str(i) 
        distances = self.calculate_box_distances(objects_list) 

        return distances 

    def process(self, cv_image, objects_list, post_processing_data): 
        post_processing_data["distances"] = self.calculate_distancing(objects_list) 
        post_processing_data["violating_objects"] = extract_violating_objects( 
            post_processing_data["distances"], self.dist_threshold) 
        post_processing_data["dist_threshold"] = self.dist_threshold 
        return cv_image, objects_list, post_processing_data 
