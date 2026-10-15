#pragma once
#include "execution_guard.h"
#include "coordinator.h"
namespace route_u {
// One synchronous operation, never borrowed across callbacks. Nested calls on
// this task are admitted; reentrant Start is refused until every guard retires.
class Mutation {
 execution::TryGuard lock_;bool admitted_;
 public:Mutation():admitted_(bool(lock_)&&enterMutation()){}
 ~Mutation(){if(admitted_)leaveMutation();}
 explicit operator bool()const{return admitted_;}
 Mutation(const Mutation&)=delete;Mutation& operator=(const Mutation&)=delete;
};
}
