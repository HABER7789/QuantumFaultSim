# Roadmap

Future enhancements and research directions for the simulator:

## Near Term
- [ ] **Full Precision Sweep**: Run a comprehensive 10^6 shot sweep to obtain high-precision threshold estimates.
- [ ] **BP-OSD Decoder Integration**: Add support for Belief-Propagation with Ordered Statistics Decoding (BP-OSD) via the `bposd` package to compare decoding performance against MWPM.
- [ ] **Phenomenological Noise Comparison**: Implement a threshold comparison between phenomenological and circuit-level noise models.

## Long Term (Advanced HPC & Physics)
- [ ] **Slurm / MPI Integration**: Provide a `run_slurm.sh` shell script or MPI hooks to support distributed execution across HPC clusters.
- [ ] **Biased Noise Models**: Test the surface code under biased noise models where dephasing (Z errors) occur at higher rates than bit-flips (X errors).
- [ ] **Alternative Codes**: Implement the `XZZX` surface code and benchmark its performance under biased noise against the standard surface code.
