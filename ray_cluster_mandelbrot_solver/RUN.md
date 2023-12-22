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


To set up and test communication between your Dockerized Ray application on a Mac and a VM (using Multipass), you need to ensure that the VM is correctly configured to communicate over the network. Multipass typically uses NAT mode by default, which allows the VM to access external networks through the host machine. Here's how to proceed:

### 1. Set Up Multipass VM

1. **Install Multipass:** If you haven't already, install Multipass on your Mac.
   
2. **Launch a VM:** Use Multipass to create a new VM. By default, it should be set up with NAT networking.
   ```bash
   multipass launch --name ray-vm
   ```

3. **Access the VM:** 
   ```bash
   multipass shell ray-vm
   ```

4. **Install Docker in the VM:** If you plan to run your application in Docker inside the VM, install Docker in the VM.
   ```bash
   sudo apt-get update
   sudo apt-get install docker.io
   ```

### 2. Network Configuration

Multipass VMs are usually configured with NAT out of the box, which means they can access external networks (like the internet) via the host machine. However, for direct communication between your host (Mac) and the VM, you might need to set up port forwarding.

1. **Find the VM's IP Address:** 
   Inside the VM, use `ip addr` or `ifconfig` to find its IP address.

2. **Set Up Port Forwarding:** 
   You need to forward the relevant ports from your host to the VM. Multipass supports port forwarding through its command line. For example:
   ```bash
   multipass mount <shared-folder> ray-vm:/<mount-point>
   multipass exec ray-vm -- sudo <command>
   ```
   Replace `<shared-folder>`, `<mount-point>`, and `<command>` with appropriate values.

### 3. Run Your Application

1. **On Your Mac:** Run your Dockerized application as you've been doing.
   
2. **On the VM:** 
   - Transfer your application files to the VM or clone from a repository.
   - Make sure to adjust the configuration to join the Ray cluster (e.g., updating `action.yaml` with the head node's IP address).

### 4. Test the Communication

1. **From the VM:** Try to connect to your application running on the host or vice versa. This could be as simple as accessing a web service or more complex like joining a Ray cluster.

2. **Monitor Ray Dashboard:** If you've set up a Ray cluster, use the Ray dashboard to monitor if the VM node successfully joins the cluster and participates in computation.

### 5. Troubleshooting

- **Firewall Settings:** Ensure that no firewall settings on your Mac or within the VM are blocking the necessary ports.
- **Correct IP Addresses:** Verify that you're using the correct IP addresses and port numbers in your configurations.
- **Network Accessibility:** Ensure both the host and VM are on the same network and can communicate with each other.

By following these steps, you should be able to set up and test communication between your Dockerized application on your Mac and a VM using Multipass in NAT mode.