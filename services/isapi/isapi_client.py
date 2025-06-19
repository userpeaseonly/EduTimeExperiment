import httpx
import json
import os
from httpx import DigestAuth



class ISAPIService:
    BASE_URL = os.environ.get("DEVICE_GATEWAY_URL", "asdf")
    username = os.environ.get("DEVICE_GATEWAY_USERNAME", "asdf")
    password = os.environ.get("DEVICE_GATEWAY_PASSWORD", "asddf")
    if not username or not password:
        raise ValueError("DEVICE_GATEWAY_USERNAME or DEVICE_GATEWAY_PASSWORD environment variable is not set.")
    if not BASE_URL:
        raise ValueError("BASE_URL environment variable is not set.")
    AUTH = DigestAuth(username, password)

    def __init__(self, terminal_id: str = None):
        self.client = httpx.Client(auth=self.AUTH, timeout=90.0)
        
    def _post(self, endpoint: str, data: dict) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            return {"error": "Request error", "details": str(e)}
    
    def _post_files(self, endpoint: str, data: dict = None, files: dict = None) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.client.post(url, json=data, files=files)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            return {"error": "Request error", "details": str(e)}

    
    def _get(self, endpoint: str, data: str = None) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            return {"error": "Request error", "details": str(e)}
    
    def _put(self, endpoint: str, data: dict) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.client.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            return {"error": "Request error", "details": str(e)}

    def get_all_devices(self) -> dict:
        endpoint = "ContentMgmt/DeviceMgmt/deviceList?format=json"
        payload = {
            "SearchDescription": {
                "position": 0,
                "maxResult": 100,
                "Filter": {
                    "key": "",
                    "devType": "",
                    "protocolType": ["ehomeV5"],
                    "devStatus": ["online", "offline"]
                }
            }
        }
        return self._post(endpoint, payload)
    
    def get_users_from_device(self, device_id: str) -> dict:
        endpoint = f"AccessControl/UserInfo/Search?format=json&devIndex={device_id}"
        payload = {
            "UserInfoSearchCond": {
                "searchID": "C7E71364-4560-0001-6EDD-16ED17B01CCD",
                "searchResultPosition": 0,
                "maxResults": 30
            }
        }
        return self._post(endpoint, payload)

    def add_person(self, device_id: str, name: str, employee_no: str) -> dict:
        endpoint = f"AccessControl/UserInfo/Record?format=json&devIndex={device_id}"
        payload = {
            "UserInfo": [
                {
                    "employeeNo": employee_no,
                    "name": name,
                    "Valid": {
                        "beginTime": "2020-01-01T00:00:00",
                        "endTime": "2030-12-31T23:59:59"
                    }
                }
            ]
        }
        return self._post(endpoint, payload)
    
    def delete_user(self, device_id: str, emp_no: str):
        endpoint = f"AccessControl/UserInfoDetail/Delete?format=json&devIndex={device_id}"
        payload = {
            "UserInfoDetail": {
                "mode": "byEmployeeNo",
                "EmployeeNoList": [
                    {
                        "employeeNo": emp_no
                    }
                ]
            }
        }
        return self._put(endpoint, payload)
    
    def delete_persons(self, device_id: str, *emp_nos: str) -> dict:
        endpoint = f"AccessControl/UserInfo/Delete?format=json&devIndex={device_id}"
        payload = {
            "UserInfoDelCond": {
                "EmployeeNoList": [
                    {
                        "employeeNo": emp_no
                    } for emp_no in emp_nos
                ]
            }
        }
        return self._put(endpoint, payload)
    
    def total_number_of_user(self, device_id: str) -> dict:
        endpoint = f"AccessControl/UserInfo/Count?format=json&devIndex={device_id}"
        return self._get(endpoint, {})
    
    def add_user_face(self, device_id: str, employee_no: str, image_path: str) -> dict:
        """ Uploads a face image for a specific user """
        endpoint = f"Intelligent/FDLib/FaceDataRecord?format=json&devIndex={device_id}"
        face_data = {
            "FaceInfo": {
                "employeeNo": employee_no,
                "faceLibType": "blackFD",
            }
        }
        boundary = "---------------------------7e13971310878"
        multipart_data = f"--{boundary}\r\n"
        multipart_data += 'Content-Disposition: form-data; name="FaceDataRecord"\r\n'
        multipart_data += "Content-Type: application/json\r\n\r\n"
        multipart_data += json.dumps(face_data) + "\r\n"
        multipart_data += f"--{boundary}\r\n"
        multipart_data += 'Content-Disposition: form-data; name="FaceImage"; filename="face.jpg"\r\n'
        multipart_data += "Content-Type: image/jpeg\r\n\r\n"
        
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()
        
        multipart_data = multipart_data.encode() + image_data + f"\r\n--{boundary}--\r\n".encode()
        
        headers = {
            "Accept": "text/html, application/xhtml+xml",
            "Accept-Language": "en-US",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "Keep-Alive",
            "Cache-Control": "no-cache"
        }
        
        response = self.client.post(f"{self.BASE_URL}{endpoint}", headers=headers, content=multipart_data)
        
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            return {"error": "Request error", "details": str(e)}
    
    def delete_user_face(self, device_id: str, *emp_nos: str) -> dict:
        """ Deletes face images for a specific user """
        endpoint = f"Intelligent/FDLib/FDSearch/Delete?format=json&devIndex={device_id}"
        payload = {
            "FaceInfoDelCond": {
                "EmployeeNoList": [
                    {
                        "employeeNo": emp_no
                    } for emp_no in emp_nos
                ]
            }
        }
        return self._put(endpoint, payload)

    def unlock_all_fucking_doors(self, device_id: str) -> dict:
        """ Unlocks all doors """
        endpoint = f"AccessControl/AcsWorkStatus?format=json{device_id}"
        payload = {
            "DoorOperation": {
                "doorIndex": 0,
                "cmd": "unlock"
            }
        }
        return self._put(endpoint)
    
    def get_events_deprecated(self, device_id: str) -> dict:
        endpoint = f"AccessControl/AcsEvent?format=json&devIndex={device_id}"
        payload = {
            "AcsEventCond": {
                "searchID": "123",
                "searchResultPosition": 100,
                "maxResults": 30,
                "major": 5,
                "minor": 0
            }
        }
        return self._post(endpoint, payload)

    def get_events(self, device_id: str = ..., position: int = 0, max_results: int = 30) -> dict:
        endpoint = f"AccessControl/AcsEvent?format=json&devIndex={device_id}"
        payload = {
            "AcsEventCond": {
                "searchID": "123",
                "searchResultPosition": position,
                "maxResults": max_results,
                "major": 5,
                "minor": 0,
                "timeReverseOrder": True
            }
        }
        return self._post(endpoint, payload)
    
    def get_device_info(self, device_name: str) -> dict:
        endpoint = "ContentMgmt/DeviceMgmt/deviceList?format=json"
        payload = {
            "SearchDescription": {
                "position": 0,
                "maxResult": 100,
                "Filter": {
                    "key": "",
                    "devType": "AccessControl",
                    "protocolType": [
                        "ehomeV5"
                    ],
                    "devStatus": [
                        "online",
                        "offline"
                    ],
                    "EhomeParams": {
                        "EhomeID": device_name
                    }
                }
            }
        }
        return self._post(endpoint, payload)


    def close(self):
        self.client.close()
