This repository contains a network simulation program designed to analyze network behavior, along with custom topology definitions for Mininet. Below is an overview of the included components:

  Network Simulation Program (Net Class):
      The Net class provides functionalities to simulate and analyze network behavior using Mininet and various network tools.
      It includes methods for starting and stopping the network, monitoring traffic, simulating attacks and regular traffic, visualizing data, and more.
      The main functionality is encapsulated in the run() method, which executes a predefined sequence of actions to simulate network behavior.

  Custom Topology Definition (CustomTopology Class):
      The CustomTopology class defines a custom network topology using Mininet's Topo class.
      It specifies a topology with one root switch and two additional switches on the first level, along with four hosts connected to these switches.
      The topology is built using the build() method, which adds switches, hosts, and establishes links between them.

  Main Program (main):
      The main program instantiates the Net class and executes its run() method to simulate network behavior.
      It imports the Net module and creates an instance of the Net class, then calls the run() method to start the simulation.

Usage:

  To run the network simulation program, execute the main script.
  Ensure that Mininet is properly configured and installed on your system before running the simulation.

Notes:

  Adjust parameters and timing as needed in the network simulation program to fit specific requirements.
  Modify the custom topology definition to create different network configurations for simulation purposes.
  Ensure proper setup and dependencies before running the simulation program.
