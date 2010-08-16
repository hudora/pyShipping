cdef extern:
    void binpack3d(int n, int W, int H, int D,
                   int *w, int *h, int *d, 
                   int *x, int *y, int *z, int *bno,
                   int *lb, int *ub, 
                   int nodelimit, int iterlimit, int timelimit, 
                   int *nodeused, int *iterused, int *timeused) nogil


def binpack(binsize, sizes, nodelimit=5000, iterlimit=5000, timelimit=2, robotpackable=False):
    cdef int numelements, box_w, box_h, box_d
    cdef int w_input[100], h_input[100], d_input[100]
    cdef int w_output[100], h_output[100], d_output[100]
    cdef int boxno[100], lowerbound, upperbound
    # cdef int nodelimit, int iterlimit, int timelimit
    cdef int nodeused, iterused, timeused
    cdef int packingtype

    if robotpackable:
        packingtype = 1
    numelements = len(sizes)
    box_w, box_h, box_d = sorted([int(x) for x in binsize])
    sizes = sizes[:100]
    for i, box in enumerate(sorted([sorted([int(x) for x in m]) for m in sizes], reverse=True)):
        w_input[i], h_input[i], d_input[i] = box

    with nogil: # release global interpreter lock to allow threading
        binpack3d(numelements, box_w, box_h, box_d,
                    w_input, h_input, d_input,
                    w_output, h_output, d_output,
                    boxno, &lowerbound, &upperbound, 
                    nodelimit, iterlimit, timelimit, 
                    &nodeused, &iterused, &timeused)
    retboxes = []
    boxcount = 1
    for i in range(numelements):
        retboxes.append(((w_input[i], h_input[i], d_input[i]), boxno[i], (w_output[i], h_output[i], d_output[i])))
        if boxno[i] > boxcount:
            boxcount = boxno[i]
    return boxcount, retboxes, dict(lowerbound=lowerbound, upperbound=upperbound, 
                                    nodeused=nodeused, iterused=iterused, timeused=timeused)
    