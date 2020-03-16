var data = self.data;
if (data.memory) {
  Tiff.initialize({ TOTAL_MEMORY: data.memory });
}
var xhr = new XMLHttpRequest();
xhr.open('GET', data.url, false);
xhr.responseType = 'arraybuffer';
xhr.send(null);
if(xhr.status !== 200){
  throw new Error('Failed to get data from ' + data.url);
}

// var tiff = new Tiff({buffer: xhr.response});
// var image = tiff.readRGBAImage();
// self.res = { image: image, width: tiff.width(), height: tiff.height() };
var ifds = UTIF.decode(xhr.response);
UTIF.decodeImage(xhr.response, ifds[0])
var image  = UTIF.toRGBA8(ifds[0]);  // Uint8Array with RGBA pixels
self.res = { image: image, width: ifds[0].width, height: ifds[0].height };