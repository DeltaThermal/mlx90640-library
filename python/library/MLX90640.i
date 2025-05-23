%module MLX90640
%include "stdint.i"

%{
int setup(int fps);
void cleanup(void);
float * get_frame(void);
uint16_t * read_registers(uint16_t start_address, uint16_t num_registers);
%}

%typemap(out) float *get_frame %{
    $result = PyList_New(768);
    for (int i = 0; i < 768; ++i) {
        PyList_SetItem($result, i, PyFloat_FromDouble($1[i]));
    }
%}


%typemap(argout) uint16_t * read_registers %{
    // Already handled in the out typemap
%}

%typemap(out) uint16_t * read_registers %{
    if ($1 == NULL) {
        $result = Py_None;
        Py_INCREF(Py_None);
    } else {
        int num_regs = (int)arg2; // num_registers is the second argument
        $result = PyList_New(num_regs);
        for (int i = 0; i < num_regs; ++i) {
            PyList_SetItem($result, i, PyLong_FromLong($1[i]));
        }
    }
%}

int setup(int fps);
void cleanup(void);
float * get_frame(void);
uint16_t * read_registers(uint16_t start_address, uint16_t num_registers);
