### On the Head Node (MacOS for example)
1. **Initial Setup:**
   - Ensure Ray is installed.
   - Place `action.yaml` in the same directory as `app.py`.
   - In `action.yaml`, set `action` to `"c"` for create.

2. **Run the Script:**
   - Execute `app.py`.
   - The script will read `action.yaml`, initialize Ray as a head node, and start the Flask app.

### On the Worker Nodes (VMs)
1. **Prepare Each VM:**
   - Install Ray and copy both `app.py` and `action.yaml` to each VM.

2. **Configure `action.yaml`:**
   - Modify `action.yaml` on each VM:
     - Set `action` to `"j"` for join.
     - Update `head_node_ip` to the IP address of your Mac.

3. **Run the Script:**
   - Execute `app.py` on each VM.
   - The script will read the updated `action.yaml`, and the VM will join the Ray cluster as a worker node.

### Testing the Cluster
- **Generate Video:** Access the `/generate_video` endpoint from a web browser or a tool like `curl` to invoke the video generation. This process should distribute the workload across the Ray cluster.
- **Monitor Cluster:** Use the Ray dashboard (typically at `http://<head_node_ip>:8265`) to monitor cluster activity and confirm that tasks are being distributed among the head and worker nodes.

### Important Notes
- **Network Configuration:** Ensure all machines are on the same network and can communicate with each other. The head node IP should be reachable from the VMs.
- **Firewall and Security:** Make sure the necessary ports (default is 6379 for Ray and 5010 for Flask) are open and not blocked by firewalls.
- **Ray Version:** Keep the Ray version consistent across all machines in the cluster.
- **Error Handling:** Consider adding error handling in your script for situations like failed Ray initialization or configuration file reading issues.

With this setup, your Ray cluster should automatically form with your Mac as the head node and the VMs as worker nodes when you run the script on each machine.