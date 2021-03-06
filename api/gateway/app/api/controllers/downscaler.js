const apiAdapter = require('../../utils/apiAdapter');
var FormData = require('form-data'); // to create multipart/form-data
var fs = require('fs'); // nodeJS file system module
var del = require('delete'); 


const BASE_URL = process.env.VIDEO_DOWNSCALER_URL;
const api = apiAdapter(BASE_URL);

const BASE_URL_PROCESSOR = process.env.IMAGE_PROCESSOR_URL;
const api_processor = apiAdapter(BASE_URL_PROCESSOR);

module.exports = {

    downscale: function(req, res, next){

        const file = req.files;
  
        let form = new FormData();
        file.forEach(element => {
          form.append('video', element.buffer, element.originalname);
        });
      
      
        api
        .post('api'+req.path, form, {'maxContentLength': Infinity, 'maxBodyLength': Infinity, responseType: "stream", headers:{'Content-Type': `multipart/form-data; boundary=${form._boundary}`}}).then(resp=>{

            var w = fs.createWriteStream("video/video.mp4"); // write video to file system

            resp.data.pipe(w);

            w.on('finish', function(){ // wait to finsh createWriteStream
                
                const form_data = new FormData();
                form_data.append('video', fs.createReadStream("video/video.mp4"), 'video.mp4');

                api_processor.post('api/v1/preprocess', form_data, {'maxContentLength': Infinity, 'maxBodyLength': Infinity, headers:{'Content-Type': `multipart/form-data; boundary=${form_data._boundary}`}}).then(resp=>{
                    return res.send(resp.data);
                })
                .then(resp=>{
                    del.sync(['video/video.mp4']) // delete temp video after sending response
                })
                .catch(error =>{
                    console.log(error);
                    res.status(400).send({'status':'Bad Request', 'error' : error.meessage})
                });
            });
        })
        .catch(error =>{
            console.log(error);
            res.status(400).send({'status':'Bad Request', 'error' : error.meessage})
        })

    }
}