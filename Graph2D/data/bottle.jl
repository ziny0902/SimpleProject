using Delaunay
function flatten(A::AbstractVector)::Matrix
    N = length(A)
    @assert N > 0
    D = length(A[1])
    @assert D > 0
    T = typeof(A[1][1])
    B = Array{T}(undef, N, D)
    for n in 1:N
        @assert length(A[n]) == D
        for d in 1:D
            B[n, d] = A[n][d]
        end
    end
    return B
end
function f(u, v)
    if v < pi
        x = (2.5 - 1.5*cos(v))*cos(u)
        y = (2.5 - 1.5*cos(v))*sin(u)
        z = -2.5*sin(v)
    elseif v < 2*pi
        x = (2.5 - 1.5*cos(v))*cos(u)
        y = (2.5 - 1.5*cos(v))*sin(u)
        z = 3*v - 3*pi
    elseif v < 3*pi
        x = -2+(2+cos(u))*cos(v)
        y = sin(u)
        z = (2+cos(u))*sin(v) + 3*pi
    else
        x = -2 + 2*cos(v) - cos(u)
        y = sin(u)
        z = -3*v + 12*pi
    end
    # x =u * sin(u) * cos(v)
    # y =  u * cos(u) * cos(v)
    # z i u * sin(v)
    return x, y, z
end
max_u = 2*pi
max_v = 4*pi
step = 0.3
uv = [[u, v] for u in 0:step:max_u+step for v in 0:step:max_v+step]
uv = flatten(uv)
mesh = delaunay(uv)
fd = open("bottle.csv", "w") 
write(fd, "# y z\n")
r, c = size(mesh.simplices)
for i in 1:r
    for j in 1:c
        u = mesh.points[mesh.simplices[i, j], 1]
        v = mesh.points[mesh.simplices[i, j], 2]
        x, y, z = f(u, v)
        write(fd, "$x $y $z\n")
    end
end
close(fd)
