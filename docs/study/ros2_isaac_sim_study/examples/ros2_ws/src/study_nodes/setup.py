from glob import glob
from setuptools import find_packages, setup
setup(
    name="study_nodes", version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/study_nodes"]),
        ("share/study_nodes", ["package.xml"]),
        ("share/study_nodes/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"], zip_safe=True,
    maintainer="Study Maintainer", maintainer_email="developer@example.invalid",
    description="Adapter testbed teaching nodes", license="Apache-2.0",
    entry_points={"console_scripts": [
        "amr_server = study_nodes.amr_server:main",
        "move_client = study_nodes.move_client:main",
        "state_watch = study_nodes.state_watch:main",
    ]},
)
