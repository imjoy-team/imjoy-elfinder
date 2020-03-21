var data = self.data;
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
var tiffData = xhr.response
if(data.name.endsWith('.gz')){
  tiffData = pako.inflate(tiffData)
}

var ifds = UTIF.decode(tiffData);
UTIF.decodeImage(tiffData, ifds[0])
var image  = UTIF.toRGBA8(ifds[0]);  // Uint8Array with RGBA pixels
self.res = { image: image, width: ifds[0].width, height: ifds[0].height };