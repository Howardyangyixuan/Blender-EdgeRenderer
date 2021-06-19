# encoding:utf-8
import os


class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class MyFile(object):
    folders = []
    outFolders = []
    count = 0

    def get_folder_paths(self, base_path):
        """
        获取文件夹下所有含有obj文件的文件夹路径
        :param base_path:
        :return:
        """
        self.folders.append(base_path)
        files = os.listdir(base_path)
        contain_obj = False
        for file in files:
            file_path = os.path.join(base_path, file)
            if os.path.isdir(file_path):
                self.get_folder_paths(file_path)
                print(file_path)
                self.folders.append(file_path)
            elif os.path.isfile(base_path + file):
                contain_obj = True
        if contain_obj is not True:
            self.folders.remove(base_path)

    def get_obj_filenames(self, folder_path):
        filenames = []
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) and file[-3:] == "obj":
                print("file:", file)
                filenames.append(file)
                self.count += 1
        return filenames

    def get_out_folders(self):
        for folder in self.folders:
            folder = folder.replace('/ABC/obj','/ABC/obj_center')
            self.outFolders.append(folder)
            # new_folder = './center_result'
            # print('here')
            # self.outFolders.append(new_folder)
            # print(new_folder)
            print("hi",folder)
            # if not os.path.exists(new_folder):
            #     os.makedirs(new_folder)
            if not os.path.exists(folder):
                os.makedirs(folder)


class MyNormalize(object):
    def __init__(self):
        self.minP = Point(1000, 10000, 10000)
        self.maxP = Point(0, 0, 0)

    def get_bounding_box(self, p):
        """
        获取物体的最小x,y,z和最大的x,y,z
        :param p:
        :return:
        """
        self.minP.x = p.x if p.x < self.minP.x else self.minP.x
        self.minP.y = p.y if p.y < self.minP.y else self.minP.y
        self.minP.z = p.z if p.z < self.minP.z else self.minP.z
        self.maxP.x = p.x if p.x > self.maxP.x else self.maxP.x
        self.maxP.y = p.y if p.y > self.maxP.y else self.maxP.y
        self.maxP.z = p.z if p.z > self.maxP.z else self.maxP.z

    def get_bounding_box_length(self):
        """
        获取包围盒的最大长度
        :return:
        """
        box_len = self.maxP.x - self.minP.x
        if box_len < (self.maxP.y - self.minP.y):
            box_len = self.maxP.y - self.minP.y
        if box_len < (self.maxP.z - self.minP.z):
            box_len = self.maxP.z - self.minP.z
        return box_len

    def do_normalize(self, box_len, points):
        """
        归一化处理
        :param center_p: 物体的中心点
        :param box_len: 包围盒的一半
        :param points:要进行归一化处理的点
        :return:
        """
        new_points = []
        for point in points:
            # x = (point.x - self.minP.x) * 2 / box_len - 1
            # y = (point.y - self.minP.y) * 2 / box_len - 1
            # z = (point.z - self.minP.z) * 2 / box_len - 1
            x = (point.x - (self.minP.x + self.maxP.x)/2.0) / box_len
            y = (point.y - (self.minP.y + self.maxP.y)/2.0) / box_len 
            z = (point.z - (self.minP.z + self.maxP.z)/2.0) / box_len
            # x = (point.x - (self.minP.x + self.maxP.x)/2.0) 
            # y = (point.y - (self.minP.y + self.maxP.y)/2.0) 
            # z = (point.z - (self.minP.z + self.maxP.z)/2.0)
            # x = point.x 
            # y = point.y
            # z = point.z
            new_points.append(Point(x, y, z))
        print(self.minP.x,self.maxP.x)
        return new_points

    def read_points(self, filename):
        """
        读取一个obj文件里的点
        :param filename:
        :return:
        """
        with open(filename) as file:
            points = []
            max = 10000
            i=0
            # while i<max:
            while True:
                i+=1
                line = file.readline()
                if not line:
                    break
                strs = line.split(" ")
                if strs[0] == "v":
                    points.append(Point(float(strs[1]), float(strs[2]), float(strs[3])))
                if strs[0] == "vt":
                    break
        return points

    def write_points(self, points, src_filename, des_filename):
        """
        将归一化好的点保存到另一个文件
        :param points:
        :param src_filename:
        :param des_filename:
        :return:
        """
        point_lines = []
        for point in points:
            point_line = "v " + str(point.x) + " " + str(point.y) + " " + str(point.z) + "\n"
            point_lines.append(point_line)
        with open(src_filename, "r") as file:
            print(src_filename)
            outFile = open(des_filename, "w")
            print(des_filename)
            for point in points:
                point_line = "v " + str(point.x) + " " + str(point.y) + " " + str(point.z) + "\n"
                outFile.write(point_line)
                outFile.flush()
            max = 10000
            i=0
            while True:
            # while i<max:
                i+=1
                line = file.readline()
                if not line:
                    break
                strs = line.split(" ")
                if strs[0] == "f":
                    outFile.write(line)
            outFile.flush()
            outFile.close()


if __name__ == "__main__":
    myFile = MyFile()
    # basePath = "/media/yangyixuan/yyx/data_processing/stanford-shapenet-renderer/center_obj"
    basePath = "/media/yangyixuan/DATA/ABC/obj"

    myFile.get_folder_paths(basePath)
    myFile.get_out_folders()
    count = 0
    for folder in myFile.folders:
        outFolderPath = myFile.outFolders.pop(0)
        print(outFolderPath)
        objFilenames = myFile.get_obj_filenames(folder)
        for objFilename in objFilenames:
            print('new')
            myNormalize = MyNormalize()
            # 读取obj文件的坐标点
            objFilePath = os.path.join(folder, objFilename)
            points = myNormalize.read_points(objFilePath)
            for point in points:
                myNormalize.get_bounding_box(point)
            # 包围盒长度
            boxLength = myNormalize.get_bounding_box_length()
            # 归一化
            points = myNormalize.do_normalize(boxLength, points)
            # 将归一化的坐标点写入目标文件
            myNormalize.write_points(points, os.path.join(folder, objFilePath), os.path.join(outFolderPath, objFilename))
            count += 1
            print("第", count, "个执行完毕")

    print("执行结束")