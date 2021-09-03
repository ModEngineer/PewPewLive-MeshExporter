--[[
MIT License

Copyright (c) 2021 ModEngineer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
--]]
function decompresscolors(meshlist)
   for meshindex = 1, #meshlist do
      local mesh = meshlist[meshindex]
      if mesh.colors~=nil then
         local colors = mesh.colors
         mesh.colors = {}
         for color, group in pairs(colors) do
            for groupitemindex = 1,  #group do
               local groupitem = group[groupitemindex]
               if type(groupitem)=="table" then
                  for i = groupitem[1], groupitem[2] do
                     mesh.colors[i] = color
                  end
               elseif type(groupitem)=="number" then
                  mesh.colors[groupitem] = color
               end
            end
         end
         meshlist[meshindex] = mesh
      end
   end
   return meshlist
end
return decompresscolors
