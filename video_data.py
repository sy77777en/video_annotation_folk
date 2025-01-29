from camera_motion_data import CameraMotionData
from camera_setup_data import CameraSetupData
from lighting_setup_data import LightingSetupData

class VideoData:
    def __init__(self):
        self._camera_motion_data = None
        self._camera_setup_data = None
        self._lighting_setup_data = None

    @property
    def camera_motion_data(self):
        if self._camera_motion_data is None:
            raise AttributeError("camera_motion_data has not been set")
        return self._camera_motion_data

    @camera_motion_data.setter
    def camera_motion_data(self, value):
        if isinstance(value, dict):
            self._camera_motion_data = CameraMotionData.create(**value)  # Auto-create instance
        elif isinstance(value, CameraMotionData):
            self._camera_motion_data = value
        else:
            raise TypeError("camera_motion_data must be a CameraMotionData instance or a dictionary of parameters")

    @property
    def camera_setup_data(self):
        if self._camera_setup_data is None:
            raise AttributeError("camera_setup_data has not been set")
        return self._camera_setup_data

    @camera_setup_data.setter
    def camera_setup_data(self, value):
        if isinstance(value, dict):
            self._camera_setup_data = CameraSetupData.create(**value)  # Auto-create instance
        elif isinstance(value, CameraSetupData):
            self._camera_setup_data = value
        else:
            raise TypeError("camera_setup_data must be a CameraSetupData instance or a dictionary of parameters")

    @property
    def lighting_setup_data(self):
        if self._lighting_setup_data is None:
            raise AttributeError("lighting_setup_data has not been set")
        return self._lighting_setup_data

    @lighting_setup_data.setter
    def lighting_setup_data(self, value):
        if isinstance(value, dict):
            self._lighting_setup_data = LightingSetupData.create(**value)  # Auto-create instance
        elif isinstance(value, LightingSetupData):
            self._lighting_setup_data = value
        else:
            raise TypeError("lighting_setup_data must be a LightingSetupData instance or a dictionary of parameters")


def create_video_data_demo():
    video_sample = VideoData()
    from camera_motion_data import camera_motion_params_demo
    print(f"You can initialize camera_motion_data with a dictionary of parameters or a CameraMotionData instance.")
    print(f"However, you should never create a CameraMotionData instance directly without using its create() function.")
    video_sample.camera_motion_data = camera_motion_params_demo
    
    print(f"If you try to access camera_setup_data before setting it, it will raise an Error.")
    try:
        print(video_sample.camera_setup_data)
    except AttributeError as e:
        print(f"AttributeError: {e}")
        
if __name__ == "__main__":
    create_video_data_demo()