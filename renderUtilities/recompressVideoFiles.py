#!/usr/bin/env python2

# Winter Guerra <winterg@mit.edu>
# August 3nd, 2018

import fire
import glob2, glob, os, sys, re, yaml, csv, shutil, subprocess
import numpy as np
import time
import threading
import tarfile

import importlib
from flightgogglesUtils import ImageHandler as FlightGogglesUtils

cameras = ["Camera_L", "Camera_R", "Camera_D"]

def recompressVideoFiles(datasetFolder, renderFolder):
    devnull = open(os.devnull, 'wb') #python >= 2.4

    config = yaml.safe_load( file(os.path.join(datasetFolder,"trajectoryOffsets.yaml"),'r') )

    # Only select folders that we have offsets for
    # print config["unitySettings"]
    trajectoryFolders = [ traj for traj in config["unitySettings"].keys()]
    
    ############## DEBUG OVERRIDE
    #trajectoryFolders = [ "sphinx", "halfMoon", "oval", "ampersand", "dice", "bentDice", "thrice", "tiltedThrice", "winter"]
    # trajectoryFolders = [ "sphinx", "halfMoon", "oval", "ampersand"] # Batch 1
    #trajectoryFolders = ["halfMoon", "oval", "ampersand", "dice", "thrice", "tiltedThrice", "winter"]
    #trajectoryFolders = ["dice", "bentDice"] # Batch 2
    # trajectoryFolders = ["thrice", "tiltedThrice", "ampersand"] # Batch 3
    # trajectoryFolders = ["clover"] 

    print "Rendering the following trajectories: "
    print trajectoryFolders


    for trajectoryFolder in trajectoryFolders:
        
        # iterate through trajectory environments
        for experiment in config["unitySettings"][trajectoryFolder]:

            # Get Trajectory offset
            envOffsetString = ' '.join( str(num) for num in experiment["offset"])

            # Find all '*_poses_centered.csv' files in folder
            trajectoryFiles = glob2.glob( os.path.join(datasetFolder, trajectoryFolder, '**/*_poses_centered.csv') )

            # Check that this experiment is applicable to this particular subset of logs
            subsetConstraint = experiment.get("yawDirectionConstraint","")            
            trajectoryFiles = [f for f in trajectoryFiles if subsetConstraint in f]
            
            ########### Limit file to 1 trajectory
            # debugTrajectory = "yawConstant/clover_maxSpeed4p0"
            # trajectoryFiles = [traj for traj in trajectoryFiles if debugTrajectory in traj]

            # Render these trajectories
            for trajectoryFile in trajectoryFiles:

                print "========================================"
                print "Starting video compression of: " + trajectoryFile

                # Get final output folder
                outputFolder = os.path.dirname(trajectoryFile)
                
                # Clean up render folder
                shutil.rmtree(renderFolder,ignore_errors=True)
                os.makedirs(renderFolder)
		
                # untar camera tarballs to render folder
                for camName in cameras:
                    # Find camera input tarballs
                    cameraArchive = os.path.join(outputFolder, camName + "_" + experiment["name"] + ".tar")

                    # Untar to render folder
                    tar = tarfile.open(cameraArchive)
                    tar.extractall(path=renderFolder)
                    tar.close()

                
                # Create video
                flightGogglesUtils = FlightGogglesUtils(renderFolder)                    
                flightGogglesUtils.createVideo(cameras=cameras)
                
                print "Copying movie files."
                    
                # Copy movies out of the image directory
                movie_files = glob.glob(os.path.join(renderFolder,"*.mp4"))
                for file_ in movie_files:
                    filename = experiment["name"] + ".mp4"
                    shutil.copy(file_, os.path.join(outputFolder, filename))
           
    


if __name__ == '__main__':
    fire.Fire(recompressVideoFiles)
