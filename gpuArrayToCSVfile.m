function gpuArrayToCSVfile(analysis_dir)

    % Get list of job group folders
    jobsTopDir = strcat(analysis_dir, '/jobs');
    jobGroupDirs = getSubFolders(jobsTopDir);
    jobDirs = getSubFoldersGrouped(jobGroupDirs);

    % Get grandstochtrackOutput folders
    bkndFiles = {};
    for index = 1:length(jobDirs)
        %gs_dir(index) = strcat(strcat(jobDirs(index), '/'), 'grandstochtrackOutput/');
        temp = strcat(strcat(jobDirs(index), '/'), 'grandstochtrackOutput/');
        %temp{1}
        %findBkndMatFile(temp{1})
        %bkndFiles = [bkndFiles; findBkndMatFile(temp{1})];
        loadSaveArray(temp{1})
    end
    %gs_dir{1}
    %bkndFiles{1}

end

function output = getSubFolders(tempFolder)
    tempSubDirs = dir(tempFolder);
    tempSubDirs = {tempSubDirs([tempSubDirs(:).isdir]).name}';
    tempSubDirs(ismember(tempSubDirs,{'.','..'})) = [];
    for index = 1:length(tempSubDirs)
        tempSubDirs(index) = strcat(strcat(tempFolder, '/'), tempSubDirs(index));
    end
    output = tempSubDirs;
end

function output = getSubFoldersGrouped(tempFoldersCellArray)
    output = {};
    for index = 1:length(tempFoldersCellArray)
        tempOut = getSubFolders(tempFoldersCellArray{index});
        output = [output; tempOut];
    end
end

function output = findBkndMatFile(tempFolder)
    tempDirContents = dir(tempFolder);
    tempDirNames = {tempDirContents(:).name};
    strfind(tempDirNames, 'bknd');
    output = strcat(tempFolder, tempDirNames(~cellfun('isempty',strfind(tempDirNames, 'bknd'))));
end

function loadSaveArray(tempFolder)
    bkndFiles = findBkndMatFile(tempFolder);
    if length(bkndFiles) ~= 1
        if length(bkndFiles) == 0
            fprintf('WARNING: no files available with bknd string')
        else
            fprintf('WARNING: multiple files with string bknd in %s. Choosing first in cell array (%s)', tempFolder, bkndFiles{1})
        end
    else
        bkndFiles{1}
        test = load(bkndFiles{1});
        max_SNR = test.stoch_out.max_SNR;
        max_cluster = test.stoch_out.cluster.reconMax;
        dlmwrite(strcat(tempFolder, 'max_SNR.txt'), max_SNR)
        dlmwrite(strcat(tempFolder, 'max_cluster.txt'), max_cluster)
    end
end