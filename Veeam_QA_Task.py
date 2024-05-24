# Pedro Pereira - Veeam Synchronization Task (Python)
# Internal Development in QA (SDET) Team test task

import os
import shutil
import logging
import schedule
import time
import datetime

# Request and validate user input for folder and log file paths
def checkPaths():
    # Request Source Folder Path, Replica Folder Path, Log File Path
    sourceFolder = input("Insert Source Folder Path: ")
    while not (os.path.exists(sourceFolder) and os.path.isdir(sourceFolder)):
        sourceFolder = input("Please enter a valid source folder path: ")

    # Check for existence of replica folder path or allow creation of a new replica folder
    choice = input("Do you wish to create a new replica folder? (y, n): ").lower()
    while choice not in ['y', 'n']:
        choice = input("Please enter a valid option (y, n): ").lower()
    if choice == 'y':
        replicaFolder = input("Please enter a path for the new replica folder: ")
        while os.path.exists(replicaFolder):  # Ensure the path does not already exist
            replicaFolder = input("The path already exists. Please enter a valid new replica folder path: ")
        os.mkdir(replicaFolder)
    else:
        replicaFolder = input("Insert existing replica folder path: ")
        while not (os.path.exists(replicaFolder) and os.path.isdir(replicaFolder)):
            replicaFolder = input("Please enter a valid replica folder path: ")

    # Check existence of the Log File destination path
    logsFile = input("Insert log file destination path: ")
    while not os.path.exists(logsFile):
        logsFile = input("Please enter a valid log file destination path: ")

    # Request Synchronization Period
    periodTypeList = ["minute", "hour", "day"]
    periodTypeInput = input("Please choose one period type to synchronize the folders (minute, hour, day): ").lower()
    while periodTypeInput not in periodTypeList:
        periodTypeInput = input(
            "Please choose one period type to synchronize the folders (minute, hour, day): ").lower()
    syncPeriodInput = int(input(f"Please enter the synchronization period (in {periodTypeInput}s): "))

    return sourceFolder, replicaFolder, logsFile, syncPeriodInput, periodTypeInput

# Synchronize folders by copying files from source to replica
def synchronizeFolders(sourceFolder, replicaFolder, logsPath):
    # Get source and replica folders names
    sourceFolderName = os.path.basename(sourceFolder)
    replicaFolderName = os.path.basename(replicaFolder)

    # Create Log file
    log_file_path = os.path.join(logsPath, f'{sourceFolderName}_LogFile.log')
    logging.basicConfig(filename=log_file_path,
                        filemode='w',
                        format='%(asctime)s - %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S',
                        level=logging.DEBUG)  # Set logging level to DEBUG
    logger = logging.getLogger(__name__)
    logger.info(f'Started Folder Synchronization of Source "{sourceFolderName}" and Replica "{replicaFolderName}"')
    print(f'Started Folder Synchronization of Source "{sourceFolderName}" and Replica "{replicaFolderName}"')

    # Delete files from replica folder
    for file in os.listdir(replicaFolder):
        file_path = os.path.join(replicaFolder, file)  # Full path to the file
        os.remove(file_path)
        logger.debug(f'Deleted file "{file}" from replica folder "{replicaFolderName}"')
        print(f'Deleted file "{file}" from replica folder "{replicaFolderName}"')

    # Copy files from the source folder to the replica folder
    for file in os.listdir(sourceFolder):
        file_path = os.path.join(sourceFolder, file)
        logger.debug(f'Copying file "{file}" from "{sourceFolderName}" to "{replicaFolderName}"')
        print(f'Copying file "{file}" from "{sourceFolderName}" to "{replicaFolderName}"')
        shutil.copy(file_path, replicaFolder)

    logger.info(f'Finished synchronizing folders "{sourceFolderName}" and "{replicaFolderName}"')
    print(f'Finished synchronizing folders "{sourceFolderName}" and "{replicaFolderName}"')


def main():

    while True:
        # Get paths and Synchronize folders
        sourceFolder, replicaFolder, logsPath, syncPeriod, periodType = checkPaths()
        synchronizeFolders(sourceFolder, replicaFolder, logsPath)

        # Schedule folder synchronization based on user input
        if periodType == "minute":
            schedule.every(syncPeriod).minutes.do(lambda: synchronizeFolders(sourceFolder, replicaFolder, logsPath))
        elif periodType == "hour":
            schedule.every(syncPeriod).hours.do(lambda: synchronizeFolders(sourceFolder, replicaFolder, logsPath))
        elif periodType == "day":
            schedule.every(syncPeriod).days.at(datetime.datetime.now().strftime("%H:%M")).do(
                lambda: synchronizeFolders(sourceFolder, replicaFolder, logsPath))
        # Added option for multiple Source-Replica Folders Synchronization
        choice = input("Do you wish to synchronize another folder? (y, n): ").lower()
        if choice != 'y':
            break

    # Start Folder Synchronization
    while True:
        # Run scheduled tasks
        schedule.run_pending()
        time.sleep(1)  # Sleep for a short duration to prevent high CPU usage


if __name__ == "__main__":
    main()
