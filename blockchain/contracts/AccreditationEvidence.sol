// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AccreditationEvidence
/// @notice Academic prototype: stores ONLY the SHA-256 hash and metadata of an
///         evidence document (never the document itself).
contract AccreditationEvidence {
    struct Evidence {
        string evidenceId;      // e.g. "EV001"
        string documentHash;    // SHA-256 (hex) of the uploaded document
        string institutionId;   // e.g. "XIE-DEMO-001"
        uint256 timestamp;      // block timestamp of registration
        address submitter;      // account that sent the transaction
        uint256 version;        // 1, 2, 3 ...
        string status;          // "Recorded" -> "Verified" / "Requires Revision"
    }

    address public owner;
    uint256 public totalRecords;
    mapping(bytes32 => Evidence) private records;
    mapping(bytes32 => bool) private exists;

    event EvidenceRegistered(string evidenceId, uint256 version, string documentHash, uint256 timestamp);
    event EvidenceVerified(string evidenceId, uint256 version, string status);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function _key(string memory evidenceId, uint256 version) private pure returns (bytes32) {
        return keccak256(abi.encode(evidenceId, version));
    }

    /// @notice Record the hash of one version of an evidence document. Records are never overwritten.
    function registerEvidence(
        string calldata evidenceId,
        uint256 version,
        string calldata documentHash,
        string calldata institutionId
    ) external onlyOwner {
        bytes32 k = _key(evidenceId, version);
        require(!exists[k], "Version already recorded");
        records[k] = Evidence(evidenceId, documentHash, institutionId, block.timestamp, msg.sender, version, "Recorded");
        exists[k] = true;
        totalRecords += 1;
        emit EvidenceRegistered(evidenceId, version, documentHash, block.timestamp);
    }

    /// @notice Read the blockchain record of one evidence version.
    function getEvidence(string calldata evidenceId, uint256 version) external view returns (Evidence memory) {
        bytes32 k = _key(evidenceId, version);
        require(exists[k], "Evidence not found");
        return records[k];
    }

    /// @notice Update only the review status (the hash can never change).
    function verifyEvidence(string calldata evidenceId, uint256 version, string calldata status) external onlyOwner {
        bytes32 k = _key(evidenceId, version);
        require(exists[k], "Evidence not found");
        records[k].status = status;
        emit EvidenceVerified(evidenceId, version, status);
    }
}
