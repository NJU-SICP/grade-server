import io
import tarfile


def copy_to_container(files, container, dst_path):
    tar_data = io.BytesIO()
    with tarfile.open(fileobj=tar_data, mode='w') as tar:
        for filename, fileobj in files.items():
            tarinfo = tar.gettarinfo(fileobj=fileobj)
            tarinfo.name = filename
            tar.addfile(tarinfo, fileobj)

    tar_data.seek(0)
    return container.put_archive(dst_path, tar_data)


def grade(grader, files, required_files, timeout):
    for file in required_files:
        if not copy_to_container({file.filename: files[file.filename]},
                                 grader, file.container_path):
            raise RuntimeError(
                f'Fail to copy {file.filename} to the container.')
    grader.start()
    grader.wait(timeout=timeout)
    return grader.logs().decode(encoding='utf-8')
