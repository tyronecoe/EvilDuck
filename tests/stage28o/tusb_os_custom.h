#pragma once
// Supported CUSTOM OS port: deterministic copied finite queue, instrumented locks.
// No scheduler. A would-block result is recorded; it cannot prove real boundedness.
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
typedef struct {bool locked;} osal_mutex_def_t;
typedef osal_mutex_def_t* osal_mutex_t;
typedef struct {void (*interrupt)(bool);unsigned depth;} osal_spinlock_t;
#define OSAL_SPINLOCK_DEF(name,int_set) osal_spinlock_t name = {int_set,0}
typedef struct {size_t capacity,item_size,head,count;unsigned char data[4][64];bool active;} osal_queue_def_t;
typedef osal_queue_def_t* osal_queue_t;
#define OSAL_QUEUE_DEF(int_set,name,depth,type) osal_queue_def_t name = {.capacity=depth,.item_size=sizeof(type)}
void osal_task_delay(uint32_t ms);
void osal_spin_init(osal_spinlock_t*);
void osal_spin_lock(osal_spinlock_t*,bool);
void osal_spin_unlock(osal_spinlock_t*,bool);
osal_mutex_t osal_mutex_create(osal_mutex_def_t*);
bool osal_mutex_delete(osal_mutex_t);
bool osal_mutex_lock(osal_mutex_t,uint32_t);
bool osal_mutex_unlock(osal_mutex_t);
osal_queue_t osal_queue_create(osal_queue_def_t*);
bool osal_queue_delete(osal_queue_t);
bool osal_queue_receive(osal_queue_t,void*,uint32_t);
bool osal_queue_send(osal_queue_t,const void*,bool);
bool osal_queue_empty(osal_queue_t);
