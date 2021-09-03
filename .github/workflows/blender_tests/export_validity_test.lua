function cmpr_two_vertexes(test, baseline)
   if #test==2 and #baseline==2 then
      return test[1] == baseline[1] and test[2] == baseline[2]
   elseif #test==3 and #baseline==3 then
      return test[1] == baseline[1] and test[2] == baseline[2] and test[3] == baseline[3]
   else
      return false
   end
end

function find_vertex(new_vertices, target_vertex)
   for index, new_vertex in pairs(new_vertices) do
      if cmpr_two_vertexes(new_vertex, target_vertex) then
         return index
      end
   end
   return -1
end

function cmpr_colors(test, baseline) --  Checks to see if the colors are the same
   for index, color in pairs(test.colors) do
      local vertex = test.vertexes[index]
      local base_index = find_vertex(baseline.vertexes, vertex) -- Attempts to find the test's vertex in the baseline

      if base_index == -1 then
         print("cmpr_colors caused the test fail. color was: ", color, " base index not found.")
         return false
      end

      if baseline.colors[base_index] ~= color then -- Checks to see if the color tied to each vertex is the same color
         print("cmpr_colors caused the test fail. color was: ", color, " base color was: ", baseline.colors[base_index])
         return false
      end

   end
   return true
end

function cmpr_vertices(test, baseline) -- Checks to see if the vertices are the same
   for index, vertex in pairs(test.vertexes) do

      local base_index = find_vertex(baseline.vertexes, vertex) -- Attempts to find the test's vertex in the baseline

      if base_index == -1 then
         print("cmpr_vertices caused the test fail.")
         return false
      end

   end
   return true
end

function cmpr_segments(test, baseline) -- Checks to see if the segments are the same
   for base_index, base_segment in pairs(baseline.segments) do
      local validsegment = false
      for index, segment in pairs(test.segments) do
         if base_segment[1]~=base_segment[2] and segment[1]~=segment[2] and (cmpr_two_vertexes(baseline.vertexes[base_segment[1] + 1], test.vertexes[segment[1]+1]) or cmpr_two_vertexes(baseline.vertexes[base_segment[1] + 1], test.vertexes[segment[2]+1])) and (cmpr_two_vertexes(baseline.vertexes[base_segment[2] + 1], test.vertexes[segment[1]+1]) or cmpr_two_vertexes(baseline.vertexes[base_segment[2] + 1], test.vertexes[segment[2]+1])) then
            validsegment = true
            break
         end
      end
      if not validsegment then
         print("cmpr_segments caused the test fail. segment index: ", base_index)
         return false
      end
      --[[ Commenting this out because it's unnecessarily complex for the purposes of testing 2-vertex segments. The above code is enough. If uncommenting this for whatever reason, comment out the above code
      for seg_index, vertex_id in pairs(segment) do

         local vertex = test.vertexes[vertex_id + 1]
         local base_index = find_vertex(baseline.vertexes, vertex) -- Attempts to find the test's vertex in the baseline

         if base_index == -1 then
            return false
         end

         local base_segment = baseline.segments[index]
         if base_segment[seg_index] ~= base_index - 1 then
            return false
         end

      end
      --]]

   end
   return true
end

function cmpr_meshes(test, baseline)
   if test["colors"] and baseline["colors"] then
      return cmpr_colors(test, baseline) and cmpr_vertices(test, baseline) and cmpr_segments(test, baseline) and #test.colors==#baseline.colors and #test.vertexes==#baseline.vertexes and #test.segments==#baseline.segments
   elseif not (test["colors"] or baseline["colors"]) then
      return cmpr_vertices(test, baseline) and cmpr_segments(test, baseline) and #test.vertexes==#baseline.vertexes and #test.segments==#baseline.segments
   else
      print("cmpr_meshes caused the test fail.")
      return false
   end
end

if arg[1]=="0" then
   local baseline_meshes=require("decompresscolors")({{vertexes={{-5,-5,-5},{-5,-5,5},{-5,5,-5},{-5,5,5},{5,-5,-5},{5,-5,5},{5,5,-5},{5,5,5}},segments={{2,0},{0,1},{3,2},{6,2},{7,6},{4,6},{7,5},{5,4},{0,4},{5,1}},colors={['0x8080ffff']={{0,3},{5,7}},['0xff8080ff']={4}}}})
   local test_meshes=require("test")
   if cmpr_meshes(test_meshes[1], baseline_meshes[1]) then
      os.exit(0)
   else
      os.exit(1)
   end
else
   local baseline_meshes=require("./decompresscolors")({{vertexes={{-5,-5,-5},{-5,-5,5},{-5,5,-5},{-5,5,5},{5,-5,-5},{5,-5,5},{5,5,-5},{5,5,5}},segments={{2,0},{0,1},{1,3},{3,2},{6,2},{3,7},{7,6},{4,6},{7,5},{5,4},{0,4},{5,1}}},{vertexes={{26.258,33.355,31.202},{18.456,30.01,25.916},{28.052,24.063,34.433},{20.25,20.718,29.147},{32.25,31.782,23.353},{24.448,28.437,18.067},{34.044,22.49,26.584},{26.242,19.145,21.298}},segments={{2,0},{0,1},{3,2},{6,2},{7,6},{4,6},{7,5},{5,4},{0,4},{5,1}},colors={['0x8080ffff']={{0,3},{5,7}},['0xff8080ff']={4}}}})
   local test_meshes=require("test2")
   if cmpr_meshes(test_meshes[1], baseline_meshes[1]) and cmpr_meshes(test_meshes[2], baseline_meshes[2]) then
      os.exit(0)
   else
      os.exit(1)
   end
end
