FROM jupyter/minimal-notebook

USER root

RUN apt-get update && apt-get install -y tree
RUN pip install numpy pandas scikit-learn plotly
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the notebook and supporting files
COPY lesson2.1.5.ipynb /home/jovyan/notebook.ipynb
COPY binary_list.py /home/jovyan/
COPY utilities.py /home/jovyan/
COPY AdaptiveAntivirus /home/jovyan/AdaptiveAntivirus

# Set permissions
RUN chown -R jovyan:users /home/jovyan

# Remove 'pip' to prevent installing new libraries
RUN rm /opt/conda/bin/pip \
    && rm -rf /usr/bin/apt-get /usr/bin/apt \
    # && /bin/bash /bin/bash_disabled \
    && mv /usr/bin/find /usr/bin/find_disabled \
    && mv /bin/grep /bin/grep_disabled \
    && mv /bin/sed /bin/sed_disabled \
    && mv /usr/bin/awk /usr/bin/awk_disabled

USER jovyan

CMD ["start-notebook.sh", "--NotebookApp.token=", "--NotebookApp.password=", "--NotebookApp.allow_origin='*'", "--ip=0.0.0.0", "--port=8888"]

