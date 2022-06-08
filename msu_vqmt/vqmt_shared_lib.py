# This is a part of MSU VQMT Python Interface
# https://github.com/msu-video-group/vqmt_python
#
# This code can be used only with installed 
# MSU VQMT Pro, Premium, Trial, DEMO v14.1+
#
# Copyright MSU Video Group, compression.ru TEAM

import ctypes
import json
import copy
import threading
import os
import numpy as np

class VQMT_Version(ctypes.Structure):
    _fields_ = [("maj",        ctypes.c_int),
                ("min",        ctypes.c_int),
                ("rev",        ctypes.c_int),
                ("extra",      ctypes.c_char_p),
                ("edition",    ctypes.c_char_p),
                ("full",       ctypes.c_char_p),
                ("build_date", ctypes.c_char_p),
               ]

def _getStrFunc(func, type=ctypes.c_char_p):
    func.restype = type
    return func

def _mergeToDict(src, srcdst):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(srcdst[k], dict):
            _mergeToDict(v, srcdst[k])
        else:
            srcdst[k] = v


def _makeStr(text):
    if isinstance(text, str):
        return text.encode('utf-8')

    return text
            
class Invoke:
    INPUT_CB_OK = 0
    INPUT_CB_EOF = 1
    INPUT_CB_ERROR = 2
    
    EXIT_STATUS_NOT_FINISHED = 50
    EXIT_STATUS_ALL_OK = 100
    EXIT_STATUS_ERRORS = 150
    EXIT_STATUS_FAILED = 200
    EXIT_STATUS_INTERRUPTED = 300

    def __init__(self, shared_interface):
        self.shared_interface = shared_interface
        self.thread = None
        self.invoke_id = None
        self.exit_status = None
        self.err = None
        
        self.evtPrepareStart = threading.Event()
        self.evtPrepareComplete = threading.Event()
        self.evtMeasureComplete = threading.Event()
        self.evtTotalComplete = threading.Event()

    def _set_id(self, invoke_id, cbs):
        self.invoke_id = invoke_id
        self.cbs = cbs

    def _set_err(self, err):
        self.err = err

    def _event_cb(self, event_data):
        if event_data['event'] == 'PrepareStart': self.evtPrepareStart.set()
        elif event_data['event'] == 'PrepareComplete': self.evtPrepareComplete.set()
        elif event_data['event'] == 'MeasureComplete': self.evtMeasureComplete.set()

    def _checkPrepareComplete(self):
        if not self.evtPrepareComplete.is_set():
            raise ValueError("Do not try to do this before preparing is complete. Try waitPrepareComplete() on this object")

    def _checkTotalComplete(self):
        if not self.evtTotalComplete.is_set():
            raise ValueError("Do not try to do this before total complete. Try wait() on this object")

    def _checkMeasureComplete(self):
        if not self.evtMeasureComplete.is_set():
            raise ValueError("Do not try to do this before measure complete. Try waitMeasureComplete() or wait() on this object")

    def getInitError(self):
        return self.err

    def waitPrepareStart(self):
        self.evtPrepareStart.wait()

    def waitPrepareComplete(self):
        self.evtPrepareComplete.wait()

    def waitMeasureComplete(self):
        self.evtMeasureComplete.wait()

    def wait(self):
        self.evtTotalComplete.wait()
        return self.exit_status
            
    def start(self):
        assert self
        self.exit_status = self.shared_interface.start(self.invoke_id)
        self.evtTotalComplete.set()
        return self.exit_status

    def getExitStatus(self):
        res = self.shared_interface.func_get_exit_status(self.invoke_id)
        return None if res < 0 else res

    def computeIsFailed(self):
        return self.getExitStatus() == Invoke.EXIT_STATUS_FAILED

    def startAsynch(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.start()

    def cancel(self):
        self._checkPrepareComplete()
        self.shared_interface.func_cancel_invoke(self.invoke_id)

    def pause(self):
        self._checkPrepareComplete()
        self.shared_interface.func_pause_invoke(self.invoke_id)

    def resume(self):
        self._checkPrepareComplete()
        self.shared_interface.func_resume_invoke(self.invoke_id)

    def getColumns(self):
        self._checkPrepareComplete()
        return json.loads(self.shared_interface.func_get_invoke_columns_information_json(self.invoke_id))

    def getFiles(self):
        self._checkPrepareComplete()
        return json.loads(self.shared_interface.func_get_invoke_files_information_json(self.invoke_id))

    def getValuesAsArray(self):
        self._checkMeasureComplete()
        totalFrames = self.shared_interface.func_get_invoke_rowcount(self.invoke_id)
        if totalFrames < 0: return None

        values = np.ndarray([totalFrames, len(self.getColumns())], dtype=np.single)
        values.fill(np.nan)

        if not self.shared_interface.func_get_invoke_values_array(self.invoke_id, values.ctypes):
            return None

        return values

    def getFrameNumbersAsArray(self):
        self._checkMeasureComplete()
        totalFrames = self.shared_interface.func_get_invoke_rowcount(self.invoke_id)
        if totalFrames < 0: return None

        frames = np.ndarray([totalFrames], dtype=np.intc)

        if not self.shared_interface.func_get_invoke_frames_array(self.invoke_id, frames.ctypes):
            return None

        return frames

    def getValuesAsList(self):
        self._checkMeasureComplete()
        return json.loads(self.shared_interface.func_get_invoke_values_json(self.invoke_id))

    def getAccumulators(self):
        self._checkMeasureComplete()
        return json.loads(self.shared_interface.func_get_invoke_accumulators_json(self.invoke_id))

    def getGeneralizedInfo(self):
        self._checkTotalComplete()
        return json.loads(self.shared_interface.func_get_invoke_generalized_info_json(self.invoke_id))

    def setInputCallback(self, cb):
        def cb_wrapper(invoke_id, file, frame, data, mask, unused):
            result = cb(invoke_id, file.decode('utf-8', errors='ignore'), frame, data, mask)
            if result is None:
                return Invoke.INPUT_CB_ERROR

            return Invoke.INPUT_CB_OK if result else Invoke.INPUT_CB_EOF

        event_callback = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p)(cb_wrapper)
        self.shared_interface.func_set_invoke_input_callback(self.invoke_id, event_callback, ctypes.c_void_p())
        self.cbs.append(event_callback)

    def __bool__(self):
        return self.invoke_id >= 0
    __nonzero__ = __bool__

    def __del__(self):
        if self.invoke_id is None: return
        self.shared_interface.func_detach_invoke(self.invoke_id)

class Config:
    def __init__(self, initProperties=None):
        self.initProperties = copy.deepcopy(initProperties) if initProperties is not None else {}
        self.addedMetrics = []
        self.addedFiles = []

    def setProperties(props):
        _mergeToDict(props, self.initProperties)

    def getConfig(self):
        res = copy.deepcopy(self.initProperties)

        if 'metrics' not in res: res['metrics'] = []
        if 'files' not in res: res['files'] = []

        for obj in self.addedMetrics:
            res['metrics'].append(obj)

        for obj in self.addedFiles:
            res['files'].append(obj)

        return res

    def addMetric(self, name, variation=None, device=None, component=None, config=None, visGamma=None, visColormap=None):
        metr = {}
        if variation is None and device is None:
            metr["metric"] = name
        elif variation is not None and device is not None:
            raise ValueError("Do not specify both variation and device")
        elif variation is not None:
            metr["metric"] = {"name":name, "variation": variation}
        elif variation is not None:
            metr["metric"] = {"name":name, "device": device}

        #if component is None:
        #    raise ValueError("Specify component")

        if component is not None: metr["color"] = component
        if config is not None: metr["config"] = copy.deepcopy(config)
        if visGamma is not None: metr["vis-gamma"] = visGamma
        if visColormap is not None: metr["vis-colormap"] = visColormap

        self.addedMetrics.append(metr)

    def addFile(self, path, startFrame=0, endFrame=None, offsetType=None, stdin=False, props=None, mode=None, indexType=None, indexFile=None):
        data = {}
        if startFrame != 0 or endFrame is not None:
            data['range'] = [startFrame] if endFrame is None else [startFrame, endFrame]

        if offsetType is not None:
            data['offset_type'] = offset_type

        if mode is not None:
            data['mode'] = mode

        if indexType is not None:
            data['index'] = indexType

        if indexFile is not None:
            data['index_file'] = indexFile

        if props is not None:
            data['props'] = props

        if stdin:
            data['stdin'] = stdin

        if len(data) == 0: obj = path
        else: obj = [path, data]
        
        self.addedFiles.append(obj)

class SharedInterface:
    def __init__(self, vqmt_dll_path):
        self.dll = ctypes.cdll.LoadLibrary(vqmt_dll_path)

        self.func_get_version = _getStrFunc(self.dll.vqmt_get_version, VQMT_Version)
        self.func_get_version_json = _getStrFunc(self.dll.vqmt_get_version_json)

        self.func_init = _getStrFunc(self.dll.vqmt_init, None)

        self.func_invoke_init_with_config_json = self.dll.vqmt_invoke_init_with_config_json

        self.func_get_picture_types_json = _getStrFunc(self.dll.vqmt_get_picture_types_json)
        self.func_get_colorspaces_json = _getStrFunc(self.dll.vqmt_get_colorspaces_json)
        self.func_get_devices_json = _getStrFunc(self.dll.vqmt_get_devices_json)
        self.func_get_metrics_json = _getStrFunc(self.dll.vqmt_get_metrics_json)

        self.func_detach_invoke = _getStrFunc(self.dll.vqmt_detach_invoke, None)

        self.func_get_error = _getStrFunc(self.dll.vqmt_get_error)

        self.func_start_process = self.dll.vqmt_start_process
        self.func_cancel_invoke = _getStrFunc(self.dll.vqmt_cancel_invoke, None)
        self.func_pause_invoke = _getStrFunc(self.dll.vqmt_pause_invoke, None)
        self.func_resume_invoke = _getStrFunc(self.dll.vqmt_resume_invoke, None)

        self.func_get_invoke_columns_information_json = _getStrFunc(self.dll.vqmt_get_invoke_columns_information_json)
        self.func_get_invoke_files_information_json = _getStrFunc(self.dll.vqmt_get_invoke_files_information_json)
        self.func_get_invoke_values_json = _getStrFunc(self.dll.vqmt_get_invoke_values_json)
        self.func_get_invoke_values_array = _getStrFunc(self.dll.vqmt_get_invoke_values_array, ctypes.c_bool)
        self.func_get_invoke_frames_array = _getStrFunc(self.dll.vqmt_get_invoke_frames_array, ctypes.c_bool)
        self.func_get_invoke_rowcount = _getStrFunc(self.dll.vqmt_get_invoke_rowcount, ctypes.c_int)
        self.func_get_invoke_accumulators_json = _getStrFunc(self.dll.vqmt_get_invoke_accumulators_json)
        self.func_set_invoke_input_callback = _getStrFunc(self.dll.vqmt_set_invoke_input_callback, ctypes.c_bool)
        self.func_get_invoke_generalized_info_json = _getStrFunc(self.dll.vqmt_get_invoke_generalized_info_json)
        self.func_get_exit_status = self.dll.vqmt_get_exit_status

        self.func_check_activation      = _getStrFunc(self.dll.vqmt_check_activation, ctypes.c_bool)
        self.func_activate_pro          = _getStrFunc(self.dll.vqmt_activate_pro, ctypes.c_bool)
        self.func_activate_pro_advanced = _getStrFunc(self.dll.vqmt_activate_pro_advanced, ctypes.c_bool)
        self.func_activate_premium      = _getStrFunc(self.dll.vqmt_activate_premium, ctypes.c_bool)

        self.func_utility_copy_image      = _getStrFunc(self.dll.vqmt_utility_copy_image, None)
        self.func_utility_copy_plane      = _getStrFunc(self.dll.vqmt_utility_copy_plane, None)

        self.func_init()

    def getError(self):
        return self.func_get_error().decode('utf-8', errors='ignore')

    def activatePro(self, activation_code, old_pass=None, new_pass=None, email=None):
        if old_pass is None and new_pass is None and email is None:
            return self.func_activate_pro(_makeStr(activation_code))
        elif old_pass is not None and new_pass is not None and email is not None:
            return self.func_activate_pro_advanced(
                _makeStr(activation_code), 
                _makeStr(email), 
                _makeStr(old_pass), 
                _makeStr(new_pass))
        else:
            raise ValueError("Specify all old_pass, new_pass, email or none of them")

    def activatePremium(self, activation_code):
        return self.func_activate_premium(_makeStr(activation_code))

    def isActivated(self):
        return self.func_check_activation()

    def invoke(self, config, event_cb=None, value_cb=None):
        invoke = Invoke(self)

        def eventCbAltered(event_data, dummy):
            data = json.loads(event_data)
            invoke._event_cb(data)
            if event_cb is not None: event_cb(data)

        event_callback = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_void_p)(eventCbAltered)
        value_callback = (ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_void_p)(lambda id, frame, col, value, _ : value_cb(id, frame, col, value))
                                if value_cb is not None else ctypes.c_void_p())

        conf_json = None
        if isinstance(config, Config):
            conf_json = config.getConfig()
        elif isinstance(config, dict):
            conf_json = config

        if conf_json is None:
            raise ValueError("Specify config as a Config instance or dict")

        invoke_id = self.func_invoke_init_with_config_json(json.dumps(conf_json).encode('utf-8'), event_callback, value_callback, ctypes.c_void_p())
        invoke._set_id(invoke_id, [event_callback, value_callback])

        if not invoke:
            invoke._set_err(self.getError())

        return invoke

    def start(self, invoke_id):
        return self.func_start_process(invoke_id)

    def getVersion(self):
        return json.loads(self.func_get_version_json())

    def getVersionObject(self):
        return self.func_get_version()

    def getPictureTypes(self) :
        return json.loads(self.func_get_picture_types_json())

    def getColorspaces(self) :
        return json.loads(self.func_get_colorspaces_json())

    def getDevices(self) :
        return json.loads(self.func_get_devices_json())

    def getMetrics(self) :
        return json.loads(self.func_get_metrics_json())

    @staticmethod
    def _checkNdArray(src):
        if not isinstance(src, np.ndarray):
            raise ValueError("the object is expected to be numpy array")

    def copyImage(self, src, dst, chan_mask):
        self._checkNdArray(src)
        return self.func_utility_copy_image(src.ctypes, ctypes.c_void_p(dst), 
            ctypes.c_int(chan_mask))

    def copyPlane(self, src, dst, plane):
        self._checkNdArray(src)
        return self.func_utility_copy_image(src.ctypes, src.shape[0] * src.itemsize, ctypes.c_void_p(dst), 
            ctypes.c_int(plane))

def loadByDir(path):
    if os.name == 'nt':
        loader_file = os.path.join(path, 'vqmt_finder.dll')
        if not os.path.exists(loader_file):
            raise Exception("Loader vqmt_finder.dll is not found")

        loader = ctypes.cdll.LoadLibrary(loader_file)
        findVQMT = loader.findVQMTdll
        findVQMT.restype = ctypes.c_char_p
        path = findVQMT().decode('utf8')

        if path=='':
            raise Exception("VQMT can not be loaded")

        return SharedInterface(path)

    elif os.name == 'posix':
        vqmt_file = os.path.join(path, 'libvqmt.so')
        
        if not os.path.exists(loader_file):
            raise Exception("libvqmt.so is not found")

        return SharedInterface(vqmt_file)

    else:
        raise Exception("Unknown OS, use SharedInterface constructor instead")


def find(version_str=None):
    version = tuple(map(int, str(version_str).split('.')) if version_str is not None else [])
    if os.name == 'nt':
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\VQMT\\installations\\pro', 0, winreg.KEY_READ
            )
            all_versions = dict()

            subkeys, values, modified = winreg.QueryInfoKey(key)

            for i in range(subkeys):
                cur_key = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, cur_key)
                value, vtype = winreg.QueryValueEx(subkey, 'InstallPath')
                cur_version = tuple(map(int, cur_key.split('.')))

                if len(version) <= len(cur_version) and version != cur_version[0:len(version)]:
                    continue

                all_versions[cur_version] = value
        except OSError:
            raise Exception("Error reading registry")
        
        if len(all_versions) == 0:
            raise Exception("Can't find suitable VQMT installation")

        res = loadByDir(all_versions[max(all_versions.keys())])

    elif os.name == 'posix':
        dll_path = '/usr/lib/libvqmt.so'
        if not os.path.exists(dll_path):
            raise Exception("MSU VQMT dll was not found")

            res = SharedInterface(dll_path)

    else:
        raise Exception("Unknown OS, use SharedInterface constructor instead")

    found_ver = res.getVersionObject()
    found_ver_tup = (found_ver.maj, found_ver.min, found_ver.rev)

    if len(version) > len(found_ver_tup) or found_ver_tup[0:len(version)] != version:
        raise Exception("Found VQMT version doesn't match the requested one")

    return res