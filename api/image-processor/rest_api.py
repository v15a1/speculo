import json
import logging
import os
import traceback
import base64

from aiohttp import web

from image_processor import ImageProcessor


async def preprocess_video(request):
	try:
		reader = await request.multipart()
		
		field = await reader.next()
		filename = field.filename
		
		size = 0
		with open(os.getcwd() + '/preprocess-videos/' + filename, 'wb') as f:
			while True:
				chunk = await field.read_chunk()  # 8192 bytes by default.
				if not chunk:
					break
				size += len(chunk)
				f.write(chunk)
		
		data = await ImageProcessor().preprocess(filename=filename)
		
		response_obj = {
			'data': data
		}
		
		# return a success json response with status code 200 i.e. 'OK'
		return web.json_response(data=response_obj, status=200)
	
	except Exception as e:
		logging.exception(e)
		
		# Failed path where name is not set
		response_obj = {'error': str(e)}
		
		# return failed with a status code of 500 i.e. 'Server Error'
		return web.json_response(data=response_obj, status=500)


async def fetch_coordinates(request):
	try:
		reader = await request.multipart()
		
		field = await reader.next()
		filename = field.filename
		
		size = 0
		with open(os.getcwd() + '/coordinate-images/' + filename, 'wb') as f:
			while True:
				chunk = await field.read_chunk()  # 8192 bytes by default.
				if not chunk:
					break
				size += len(chunk)
				f.write(chunk)
		
		data = await ImageProcessor().fetch_coordinates(filename=filename)
		
		response_obj = {
			'data': data
		}
		# return a success json response with status code 200 i.e. 'OK'
		return web.json_response(data=response_obj, status=200)
	
	except Exception as e:
		logging.exception(e)
		
		# Failed path where name is not set
		response_obj = {'error': str(e)}
		
		# return failed with a status code of 500 i.e. 'Server Error'
		return web.json_response(data=response_obj, status=500)


async def generate_fingerprint(request):
	try:
		reader = await request.multipart()
		
		field = await reader.next()
		filename = field.filename
		
		size = 0
		with open(os.getcwd() + '/fingerprint-images/' + filename, 'wb') as f:
			while True:
				chunk = await field.read_chunk()  # 8192 bytes by default.
				if not chunk:
					break
				size += len(chunk)
				f.write(chunk)
		
		data = await ImageProcessor().generate_fingerprint(filename=filename)
		
		response_obj = {
			'data': data
		}
		# return a success json response with status code 200 i.e. 'OK'
		return web.json_response(data=response_obj, status=200)
	
	except Exception as e:
		logging.exception(e)
		
		# Failed path where name is not set
		response_obj = {'error': str(e)}
		
		# return failed with a status code of 500 i.e. 'Server Error'
		return web.json_response(data=response_obj, status=500)


app = web.Application()

routes = [
	web.post('/api/v1/preprocess', preprocess_video),
	web.post('/api/v1/coordinates', fetch_coordinates),
	web.post('/api/v1/fingerprint', generate_fingerprint)
]

app.add_routes(routes)

web.run_app(app)
