// Diagnostic of the actual pinned framework's pixel conversion, not a game prototype.
#define FORBIDDEN_SYMBOL_ALLOW_ALL
#include <cstdio>
#include <cstdlib>
#include "common/memstream.h"
#include "astronomica/resource.h"
#include "image/bmp.h"
#include "graphics/surface.h"

int main() {
 FILE *file=fopen("D:/astro/PLACES/P1/MEGAFILE.HYP","rb");if(!file)return 2;
 fseek(file,0,SEEK_END);long size=ftell(file);rewind(file);
 byte *bytes=(byte*)malloc(size);if(fread(bytes,1,size,file)!=size)return 3;fclose(file);
 Common::MemoryReadStream stream(bytes,size,DisposeAfterUse::NO);
 Astronomica::Scene scene;Astronomica::ResourceReader reader(stream);if(!reader.read(scene))return 4;
 printf("original P1 background offset%u bytes%u\n",scene.background.offset,scene.background.size);
 Common::MemoryReadStream bitmap(bytes+scene.background.offset,scene.background.size,DisposeAfterUse::NO);
 Image::BitmapDecoder decoder;if(!decoder.loadStream(bitmap)||!decoder.getSurface())return 5;
 printf("original bitmap %dx%d source-bpp%u palette%u\n",decoder.getSurface()->w,decoder.getSurface()->h,decoder.getSurface()->format.bytesPerPixel,decoder.getPalette().size());
 const Graphics::PixelFormat formats[]={Graphics::PixelFormat(2,5,6,5,0,11,5,0,0),Graphics::PixelFormat(2,5,5,5,0,10,5,0,0),Graphics::PixelFormat::createFormatRGB24(),Graphics::PixelFormat::createFormatARGB32()};
 for(uint i=0;i<4;++i){
  Graphics::Surface *rgb=decoder.getSurface()->convertTo(formats[i],decoder.getPalette().data(),decoder.getPalette().size());if(!rgb)return 6;
  uint nonblack=0;uint32 hash=2166136261U;
  for(int y=0;y<rgb->h;++y)for(int x=0;x<rgb->w;++x){uint8 red,green,blue;rgb->format.colorToRGB(rgb->getPixel(x,y),red,green,blue);if(red||green||blue)++nonblack;for(byte v:{red,green,blue})hash=(hash^v)*16777619U;}
  printf("format%u bpp%u nonblack%u RGBhash%08x\n",i,rgb->format.bytesPerPixel,nonblack,hash);
  rgb->free();delete rgb;
 }
 free(bytes);return 0;
}
