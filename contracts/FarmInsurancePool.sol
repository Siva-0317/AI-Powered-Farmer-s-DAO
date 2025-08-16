// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title FarmInsurancePool
 * @dev Insurance contract using ERC-20 stable tokens with binary oracle + fractional (0-1) payout percent.
 */
contract FarmInsurancePool is ReentrancyGuard, Ownable {
    IERC20 public stableToken;

    struct Policy {
        address farmer;
        address funder;
        uint256 premium;
        uint256 insuredAmount;
        uint256 startDate;
        bool active;
        bool paidOut;
        string farmLocation;
        uint256 cropType; // 0=Wheat, 1=Maize, 2=Rice.
    }

    struct OracleResult {
        bool fulfilled;
        uint8 stressLevel;         // 0=not stressed, 1=stressed
        uint256 payoutPercentage;  // fractional, scaled by 1e6 (0–1 represented as 0–1_000_000)
        uint256 timestamp;
    }

    mapping(uint256 => Policy) public policies;
    mapping(uint256 => OracleResult) public oracleResults;
    mapping(address => bool) public authorizedOracles;

    uint256 public policyCount;
    uint256 public totalPremiumsCollected;
    uint256 public totalPayoutsExecuted;

    // Events
    event PolicyCreated(
        uint256 indexed policyId,
        address indexed farmer,
        address indexed funder,
        uint256 insuredAmount,
        string farmLocation
    );
    event OracleDataReceived(
        uint256 indexed policyId,
        uint8 stressLevel,
        uint256 payoutPercentage
    );
    event PayoutExecuted(
        uint256 indexed policyId,
        address indexed farmer,
        uint256 amount
    );

    modifier onlyAuthorizedOracle() {
        require(authorizedOracles[msg.sender], "Not authorized oracle");
        _;
    }

    constructor(address _stableToken) {
        stableToken = IERC20(_stableToken);
        authorizedOracles[msg.sender] = true;
    }

    function createPolicy(
        address farmer,
        uint256 insuredAmount,
        string memory farmLocation,
        uint256 cropType,
        uint256 premiumAmount
    ) external nonReentrant {
        require(farmer != address(0), "Invalid farmer address");
        require(insuredAmount > 0, "Invalid insured amount");
        require(premiumAmount > 0, "Invalid premium amount");

        require(
            stableToken.transferFrom(msg.sender, address(this), premiumAmount),
            "Premium transfer failed"
        );

        policyCount++;

        policies[policyCount] = Policy({
            farmer: farmer,
            funder: msg.sender,
            premium: premiumAmount,
            insuredAmount: insuredAmount,
            startDate: block.timestamp,
            active: true,
            paidOut: false,
            farmLocation: farmLocation,
            cropType: cropType
        });

        totalPremiumsCollected += premiumAmount;
        emit PolicyCreated(policyCount, farmer, msg.sender, insuredAmount, farmLocation);
    }

    function submitOracleData(
        uint256 policyId,
        uint8 stressLevel,           // strictly 0 or 1
        uint256 payoutPercentage     // scaled by 1e6 (e.g., 650000 for 65%)
    ) external onlyAuthorizedOracle nonReentrant {
        require(policyId <= policyCount && policyId > 0, "Invalid policy ID");
        require(stressLevel == 0 || stressLevel == 1, "Stress level must be 0 or 1");
        require(payoutPercentage <= 1_000_000, "payoutPercentage max is 100% (1e6)");

        Policy storage policy = policies[policyId];
        require(policy.active, "Policy not active");
        require(!policy.paidOut, "Already paid out");

        oracleResults[policyId] = OracleResult({
            fulfilled: true,
            stressLevel: stressLevel,
            payoutPercentage: payoutPercentage,
            timestamp: block.timestamp
        });
        emit OracleDataReceived(policyId, stressLevel, payoutPercentage);

        // ONLY PAY OUT if stressed and insuredAmount > 0
        if (stressLevel == 1) {
            _executePayout(policyId, payoutPercentage);
        }
    }

    function _executePayout(uint256 policyId, uint256 payoutPercentage) internal {
        Policy storage policy = policies[policyId];
        
//feoifoejfoiesjofiesojei
        // Case 1: Bad data - refund premium to farmer
        if (policy.insuredAmount == 0) {
            policy.active = false;
            policy.paidOut = true;
            
            // REFUND THE PREMIUM - this is fair!
            require(
                stableToken.transfer(policy.farmer, policy.premium),
                "Premium refund failed"
            );
            emit PayoutExecuted(policyId, policy.farmer, policy.premium);
            return;
        }

        uint256 payoutAmount = (policy.insuredAmount * payoutPercentage) / 1_000_000;

        // Case 2: 0% payout - keep policy active, no payout this time
        if (payoutAmount == 0) {
            // DON'T deactivate - just log the 0% payout event
            emit PayoutExecuted(policyId, policy.farmer, 0);
            return; // Policy stays active for future stress events
        }

        // Case 3: Normal payout
        require(
            stableToken.balanceOf(address(this)) >= payoutAmount,
            "Insufficient pool balance"
        );

        policy.active = false;
        policy.paidOut = true;
        totalPayoutsExecuted += payoutAmount;

        require(
            stableToken.transfer(policy.farmer, payoutAmount),
            "Payout transfer failed"
        );

        emit PayoutExecuted(policyId, policy.farmer, payoutAmount);
    }


    function executePayout(uint256 policyId) external onlyAuthorizedOracle {
        OracleResult storage result = oracleResults[policyId];
        require(result.fulfilled, "No oracle data");
        if (result.stressLevel == 1) {
            _executePayout(policyId, result.payoutPercentage);
        }
        // If not stressed, does nothing
    }

    function fundPool(uint256 amount) external {
        require(amount > 0, "Invalid amount");
        require(
            stableToken.transferFrom(msg.sender, address(this), amount),
            "Funding transfer failed"
        );
        // No separate pool balance tracking
    }

    function authorizeOracle(address oracle) external onlyOwner {
        authorizedOracles[oracle] = true;
    }

    function revokeOracle(address oracle) external onlyOwner {
        authorizedOracles[oracle] = false;
    }

    function getPolicy(uint256 policyId) external view returns (Policy memory) {
        require(policyId <= policyCount && policyId > 0, "Invalid policy ID");
        return policies[policyId];
    }

    function getOracleResult(uint256 policyId) external view returns (OracleResult memory) {
        return oracleResults[policyId];
    }
}
