from math import inf
import os
import glob
# obj_list_path = 'center_result/test.obj/obj_list.txt'
# obj_list_path = '/media/yangyixuan/DATA/ABC/obj_list.txt'
obj_list_path = '/media/yangyixuan/DATA/ABC/obj_center_list.txt'
# out_path = '/media/yangyixuan/DATA/ABC/obj_image.txt'
out_path = '/media/yangyixuan/DATA/ABC/freestyle_image.txt'
with open(obj_list_path) as f:
    infolders = f.readlines()
    with open(out_path) as out:
        outfolders = out.readlines()
        cnt = 0
        for outfolder,infolder in zip(outfolders,infolders):
            print(infolder)
            outfolder = outfolder.strip()
            inglob = infolder.strip()+'/*.obj'
            # print(inglob)
            infile = glob.glob(inglob)[0]
            print(infile)
            # cnt+=1
            # if cnt>2:
            #     break
            # command = 'blender --background --python render_blender_single_view.py -- --views 1 --output_folder '+ outfolder+" "+infile +' --resolution=1024'
            # command = 'blender --background --python render_blender_single_view_freestyle.py -- --views 1 --output_folder '+ outfolder+" "+infile +' --resolution=1024'
            command = 'blender --background --python render_blender_single_view_freestyle.py -- --views 1 --output_folder '+ outfolder+" "+infile +' --resolution=256'
            print(command)
            os.system(command)

