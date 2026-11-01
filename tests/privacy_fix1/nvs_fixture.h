#pragma once
#include <string>
#include <vector>

// Synthetic typed NVS boundary. Immediate writes deliberately do not imply
// transactional rollback when a later set or commit fails.
namespace nvsMock {
extern unsigned reads, writes, opens, closes, commits;
extern bool fail, failCommit;
extern unsigned failWriteAt;
extern std::vector<std::string> writtenKeys;
void reset();
std::string persistedString(const char *key);
}
