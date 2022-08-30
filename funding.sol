// SPDX-License-Identifier: MIT 

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract Funding{
    using SafeMath for uint256;
    address georli_ad = 0xD4a33860578De61DBAbDc8BFdb98FD742fA7028e;
    mapping(address => uint256) public donorAddressFunds;
    address public owner;
    address[] public funders;

    constructor() {
        owner = msg.sender;
    }
    function fund() public payable{
        uint256 minRequiredUSD = 50 * 10 ** 18;
        require(convertToDollar(msg.value) >= minRequiredUSD, "$50 is the minimum cost for this product"); 
        if (donorAddressFunds[msg.sender] == 0){
            funders.push(msg.sender);
        }
        donorAddressFunds[msg.sender] += msg.value;
    }

    function withdraw() onlyOwner payable public{
        //  only admin authorized to withdraw
        payable(msg.sender).transfer(address(this).balance);
        for (uint256 funderIdx = 0; funderIdx < funders.length; funderIdx++){
            address funder = funders[funderIdx];
            donorAddressFunds[funder] = 0;
        }
        funders = new address[](0);
    }
    function getVersion() public view returns (uint256){
        AggregatorV3Interface feed = AggregatorV3Interface(georli_ad);
        return feed.version();
    }

    function getPrice() public view returns (uint256){
        AggregatorV3Interface feed = AggregatorV3Interface(georli_ad);
        (,int256 answer,,,) = feed.latestRoundData();
        return uint256(answer * 10 ** 10);
    }

    function convertToDollar(uint256 ethAmount) public view returns (uint256){
        return (getPrice() * ethAmount) / 10 ** 18;
    }
    modifier onlyOwner{
        require(msg.sender == owner);
        _;
    }
}