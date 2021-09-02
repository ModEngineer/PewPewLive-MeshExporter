
function check_lengths(file, baseline)
    if #file.colors ~= #baseline.colors then
        return false
    end
    if #file.vertexes ~= #baseline.vertexes then
        return false
    end
    if #file.segments ~= #baseline.segments then
        return false
    end
    return true
end

function find_vertex(vertices, target)
    for index, vertex in pairs(vertices) do
        if vertex[1] == target[1] and vertex[2] == target[2] then
            return index
        end
    end
    print("Not Found")
    return -1
end

function cmpr_colors(file, baseline) --  Checks to see if the colors are the same
    for index, color in pairs(file.colors) do

        local vertex = file.vertexes[index]
        local base_index = find_vertex(baseline.vertexes, vertex) -- Attempts to find the file's vertex in the baseline

        if base_index == -1 then
            return false
        end

        if baseline.colors[base_index] ~= color then -- Checks to see if the color tied to each vertex is the same color
            return false
        end

    end
    return true
end

function cmpr_vertices(file, baseline) -- Checks to see if the vertices are the same
    for index, vertex in pairs(file.vertexes) do

        local base_index = find_vertex(baseline.vertexes, vertex) -- Attempts to find the file's vertex in the baseline

        if base_index == -1 then
            return false
        end

    end
    return true
end

function cmpr_segments(file,baseline) -- Checks to see if the segments are the same
    for index, segment in pairs(file.segments) do

        for seg_index, vertex_id in pairs(segment) do

            local vertex = file.vertexes[vertex_id + 1]
            local base_index = find_vertex(baseline.vertexes, vertex) -- Attempts to find the file's vertex in the baseline

            if base_index == -1 then
                return false
            end

            local base_segment = baseline.segments[index]
            if base_segment[seg_index] ~= base_index - 1 then
                return false
            end

        end

    end
    return true
end
function cmpr_file(file, baseline)

    if not check_lengths(file, baseline) then
        return false
    end

    return cmpr_colors(file, baseline) and cmpr_vertices(file, baseline) and cmpr_segments(file, baseline)

end
