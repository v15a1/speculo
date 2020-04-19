import json
import logging
import os

import aiohttp
import numpy as np
from mongoengine import BooleanField, connect, Document, ListField, StringField


class ImageComparator:
	def __init__(self):
		self._FACE_SERVICE_ENDPOINT = os.getenv('FACE_SERVICE_URL')
	
	async def _get_all_faces(self):
		session = aiohttp.ClientSession()
		headers = {'content-type': 'application/json'}
		
		response = await session.get(self._FACE_SERVICE_ENDPOINT + "?fingerprint=true", headers=headers)
		
		data = await response.json()
		
		await session.close()
		
		if 'reason' in data.keys():
			logging.error(data['reason'])
			raise Exception("There was an getting all the faces.")
		
		return data['data']
	
	async def _save_unknown_face(self, fingerprint):
		session = aiohttp.ClientSession()
		headers = {'content-type': 'application/json'}
		
		body = json.dumps({'fingerprint': np.reshape(fingerprint, [-1, 64, 64, 3]).tolist()})
		
		response = await session.post(self._FACE_SERVICE_ENDPOINT + "/unknown", json=body, headers=headers)
		
		data = await response.json()

		await session.close()
		
		if 'reason' in data.keys():
			logging.error(data['reason'])
			raise Exception("There was an error in saving the unknown face.")
		
		return data['id']
	
	@staticmethod
	def _distance01(matrix_one, matrix_two):
		mat_one = np.array(matrix_one)
		mat_two = np.array(matrix_two)
		distance_value = np.linalg.norm(mat_one - mat_two)
		return distance_value
	
	@staticmethod
	def _distance02(matrix_one, matrix_two):
		mat_one = np.array(matrix_one)
		mat_two = np.array(matrix_two)
		return np.sqrt(np.sum((mat_one - mat_two) ** 2))
	
	def _compare(self, detected_encoding, known_face_encodings_list):
		indexes = []
		high_matches = []
		
		for index, face_encoding in enumerate(known_face_encodings_list):
			face_distance = self._distance01(detected_encoding, face_encoding)
			
			if face_distance < 0.6:
				indexes.append(index)
				high_matches.append(face_distance)
		
		if len(indexes) > 0:
			val = indexes[high_matches.index(min(high_matches))] + 1
			return val
		else:
			return "Error"
	
	async def matrix_matcher(self, matrix):
		matrix = np.array(matrix)
		saved_matrix = []
		saved_names = []
		saved_ids = []
		saved_blacklist = []
		
		faces = await self._get_all_faces()
		
		for face in faces:
			saved_matrix.append(np.reshape(list(face['matrix']), [-1]).tolist())
			saved_names.append(list(face['label']))
			saved_ids.append(list(str(face['id'])))
			saved_blacklist.append(list(str(face['blacklisted'])))
			saved_blacklist.append(list(str(face['created_at'])))
			saved_blacklist.append(list(str(face['updated_at'])))
		
		identity = self._compare(matrix, saved_matrix)
		
		if identity == "Error":
			
			face_id = await self._save_unknown_face(fingerprint=matrix)
			
			data = {
				'found': False,
				'id': str(face_id),
				'name': 'Unknown'
			}
			
			return data
		
		else:
			name_label = "".join(saved_names[identity - 1])
			face_id = "".join(saved_ids[identity - 1])
			face_blacklist = "".join(saved_blacklist[identity - 1])
			data = {
				'found': True,
				'id': face_id,
				'name': name_label,
				'blacklist': face_blacklist == "True"
			}
		
		return data
