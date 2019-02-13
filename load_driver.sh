#-+MANPATH=/cm/local/apps/cuda/libs/current/share/man:/cm/shared/apps/slurm/17.02.2/man:/usr/local/share/man:/usr/share/man/overrides:/usr/share/man:/cm/local/apps/environment-modules/current/share/man
export MANPATH=/cm/local/apps/cuda/libs/current/share/man:$MANPATH

#+CUDA_INC_PATH=/cm/shared/apps/cuda90/toolkit/9.0.176

#+CUDA_SDK=/cm/shared/apps/cuda90/sdk/9.0.176

#-+LIBRARY_PATH=/cm/local/apps/cuda/libs/current/lib64:/cm/shared/apps/cuda90/toolkit/9.0.176/lib64:/cm/shared/apps/slurm/17.02.2/lib64/slurm:/cm/shared/apps/slurm/17.02.2/lib64
export LIBRARY_PATH=/cm/local/apps/cuda/libs/current/lib64:$LIBRARY_PATH

#-+LD_LIBRARY_PATH=/cm/shared/apps/cuda90/toolkit/9.0.176/extras/CUPTI/lib64:/cm/local/apps/cuda/libs/current/lib64:/cm/shared/apps/cuda90/toolkit/9.0.176/lib64:/cm/shared/apps/slurm/17.02.2/lib64/slurm:/cm/shared/apps/slurm/17.02.2/lib64:/cm/local/apps/gcc/6.3.0/lib:/cm/local/apps/gcc/6.3.0/lib64
export LD_LIBRARY_PATH=/cm/local/apps/cuda/libs/current/lib64:$LD_LIBRARY_PATH

#-+CPATH=/cm/shared/apps/cuda90/sdk/9.0.176/common/inc:/cm/shared/apps/cuda90/toolkit/9.0.176/include:/cm/shared/apps/slurm/17.02.2/include

#+CUDA_CACHE_DISABLE=1
export CUDA_CACHE_DISABLE=1

#+CUDA_INSTALL_PATH=/cm/shared/apps/cuda90/toolkit/9.0.176

#-+PATH=/cm/local/apps/cuda/libs/current/bin:/cm/shared/apps/cuda90/sdk/9.0.176/bin/x86_64/linux/release:/cm/shared/apps/cuda90/toolkit/9.0.176/bin:/var/scratch/mutgeert/miniconda/bin:/cm/shared/apps/slurm/17.02.2/sbin:/cm/shared/apps/slurm/17.02.2/bin:/cm/local/apps/gcc/6.3.0/bin:/cm/shared/apps/torque/6.1.1/bin:/cm/shared/apps/torque/6.1.1/sbin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/usr/sbin:/cm/local/apps/environment-modules/3.2.10/bin:/home/mutgeert/.local/bin:/home/mutgeert/bin
export PATH=/cm/local/apps/cuda/libs/current/bin:$PATH

#+LD_RUN_PATH=/cm/local/apps/cuda/libs/current/lib64
export LD_RUN_PATH=/cm/local/apps/cuda/libs/current/lib64

#-+_LMFILES_=/cm/local/modulefiles/gcc/6.3.0:/cm/shared/modulefiles/slurm/17.02.2:/cm/shared/modulefiles/cuda90/toolkit/9.0.176

#-+LOADEDMODULES=gcc/6.3.0:slurm/17.02.2:cuda90/toolkit/9.0.176

#+INCLUDEPATH=/cm/shared/apps/cuda90/toolkit/9.0.176/extras/Debugger/include:/cm/shared/apps/cuda90/toolkit/9.0.176/extras/CUPTI/include:/cm/shared/apps/cuda90/toolkit/9.0.176/include/CL:/cm/shared/apps/cuda90/sdk/9.0.176/common/inc:/cm/shared/apps/cuda90/toolkit/9.0.176/include

#+PYTHONPATH=/cm/local/apps/cuda/libs/current/pynvml
export PYTHONPATH=/cm/local/apps/cuda/libs/current/pynvml

#+CUDA_ROOT=/cm/shared/apps/cuda90/toolkit/9.0.176

#+CUDA_CMLOCAL_ROOT=/cm/local/apps/cuda/libs/current
export CUDA_CMLOCAL_ROOT=/cm/local/apps/cuda/libs/current

