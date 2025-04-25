// mlx90640/bindings.cpp

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "MLX90640_API.h"

namespace py = pybind11;

PYBIND11_MODULE(_mlx90640, m) {
    m.doc() = "MLX90640 sensor bindings";

    // Expose the paramsMLX90640 struct as mlx90640.Params
    py::class_<paramsMLX90640>(m, "Params")
        .def(py::init<>());

    // dump_eeprom → numpy array of uint16_t
    m.def("dump_eeprom",
        [](uint8_t slaveAddr) {
            py::array_t<uint16_t> ee(832);
            int err = MLX90640_DumpEE(slaveAddr, ee.mutable_data());
            if (err != 0)
                throw std::runtime_error("EEPROM dump failed: " + std::to_string(err));
            return ee;
        },
        py::arg("slaveAddr"),
        "Dump the MLX90640 EEPROM (832 words) into a numpy uint16 array"
    );

    // get_frame_data → numpy array of uint16_t (834 words)
    m.def("get_frame_data",
        [](uint8_t slaveAddr) {
            py::array_t<uint16_t> frame(834);
            int err = MLX90640_GetFrameData(slaveAddr, frame.mutable_data());
            if (err < 0)
                throw std::runtime_error("Frame read failed: " + std::to_string(err));
            return frame;
        },
        py::arg("slaveAddr"),
        "Read one raw frame (834 words) into a numpy uint16 array"
    );

    // extract_parameters takes the numpy EEPROM array + Params instance
    m.def("extract_parameters",
        [](py::array_t<uint16_t, py::array::c_style | py::array::forcecast> ee,
           paramsMLX90640 &params)
        {
            if (ee.size() != 832)
                throw std::runtime_error("EEPROM array must have length 832");
            int err = MLX90640_ExtractParameters(ee.mutable_data(), &params);
            if (err != 0)
                throw std::runtime_error("Parameter extraction failed: " + std::to_string(err));
            return err;
        },
        py::arg("ee"), py::arg("params"),
        "Parse EEPROM data into a Params object"
    );

    // calculate_to takes frame array + Params + emissivity + tr + pre-allocated result array
    m.def("calculate_to",
        [](py::array_t<uint16_t, py::array::c_style | py::array::forcecast> frame,
           paramsMLX90640 &params,
           float emissivity,
           float tr,
           py::array_t<float, py::array::c_style | py::array::forcecast> result)
        {
            if (frame.size() != 834)
                throw std::runtime_error("Frame array must have length 834");
            if (result.size() != 768)
                throw std::runtime_error("Result array must have length 768");
            MLX90640_CalculateTo(frame.mutable_data(), &params, emissivity, tr, result.mutable_data());
        },
        py::arg("frame"), py::arg("params"),
        py::arg("emissivity"), py::arg("tr"), py::arg("result"),
        "Compute object temperatures into a pre-allocated float array of length 768"
    );

    // You can expose more functions similarly if needed...
}
