// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DynamicGreeting {
    // State variable for the greeting message
    string public greeting;
    // State variable to store the address of the last 
    // person who set the greeting
    address public lastSetter;

    // Constructor to set an initial greeting 
    // when the contract is deployed
    constructor(string memory _initialGreeting) {
        greeting = _initialGreeting;
        // 'msg.sender' is the address deploying the contract
        lastSetter = msg.sender; 
    }

    // Function to set a new greeting
    function setGreeting(string memory _newGreeting) public {
        greeting = _newGreeting; // Update the greeting message
        lastSetter = msg.sender;  // Update who set the greeting
    }

    // Function to get the current greeting (already 
    // created by 'public greeting')
    // Function to get the address of the last setter 
    // (already created by 'public lastSetter')
    // You can also add explicit getter functions if you prefer:
    function getGreeting() public view returns (string memory) {
        return greeting;
    }

    function getLastSetter() public view returns (address) {
        return lastSetter;
    }
}