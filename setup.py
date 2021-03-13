from setuptools import setup
import wordclock

setup(
    name='wordclock',
    version=wordclock.__version__,
    author=wordclock.__author__,
    author_email=wordclock.__author_email__,
    url=wordclock.__url__,
    license=wordclock.__license__,
    description=wordclock.__description__,

    packages=['wordclock'],
    entry_points={
        "console_scripts": [
            "calibrate=wordclock.calibrate:main",
            "tneo=wordclock.tneo:main",
            "tsense=wordclock.tsense:main",
            "wc=wordclock.wc:main",
            "send-log=wordclock.send_log:main",
            "get-update=wordclock.get_update:main",
        ]
    },
    install_requires=[]
    )
