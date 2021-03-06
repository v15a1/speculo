from aiohttp import web
import json
import logging
from yolo.yolo import YOLO
import numpy as np

yolo = YOLO(draw=False, debug=False)


async def predict(request):
    try:
        data = await request.json()
        if 'instances' not in data.keys():
            return web.Response(body=json.dumps({'error': 'instances-required'}),
                                status=400, content_type='application/json')
        data = np.array(data['instances'])
        shape = data.shape
        if len(shape) != 3:
            return web.Response(body=json.dumps({'error': 'input must be 3-dimensional, shape of the passed image is' + str(shape)}),
                                status=400, content_type='application/json')
        if shape[0] % 32 != 0 and shape[1] % 32 != 0:
            return web.Response(body=json.dumps({'error': 'image width and height must be multiple 32, shape of the passed image is' + str(shape)}),
                                status=400, content_type='application/json')
        output = yolo.detect_image_fast(data)
        return web.Response(body=json.dumps({'predictions': output.astype("uint8").tolist()}),
                            status=200, content_type='application/json')
    except Exception as e:
        logging.error('Error While Processing a request')
        logging.exception(e)
        return web.Response(body=json.dumps({'error': str(e)}),
                            status=500, content_type='application/json')


app = web.Application(client_max_size=10000000000)
app.add_routes([web.post('/v1/models/facedetector:predict', predict)])
web.run_app(app, port=8080)
