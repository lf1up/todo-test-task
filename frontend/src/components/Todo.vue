<template>
  <div class="todo-app">
    <div class="container">
      <h1 class="title">Todo App</h1>
      
      <!-- Add new task form -->
      <div class="add-task-form">
        <div class="input-group">
          <input
            v-model="newTaskText"
            @keyup.enter="addTask"
            type="text"
            placeholder="Add a new task..."
            class="task-input"
            :disabled="loading"
          />
          <button @click="addTask" :disabled="loading || !newTaskText.trim()" class="add-btn">
            Add Task
          </button>
        </div>
      </div>

      <!-- Loading indicator -->
      <div v-if="loading" class="loading">Loading...</div>

      <!-- Error message -->
      <div v-if="error" class="error">{{ error }}</div>

      <!-- Tasks list -->
      <div class="tasks-container">
        <div v-if="tasks.length === 0 && !loading" class="no-tasks">
          No tasks yet. Add one above!
        </div>
        
        <div v-for="task in tasks" :key="task.id" class="task-item">
          <div class="task-content">
            <!-- Checkbox for completion -->
            <input
              type="checkbox"
              :checked="task.is_done"
              @change="toggleTask(task)"
              class="task-checkbox"
            />
            
            <!-- Task text (editable) -->
            <div v-if="editingTaskId !== task.id" class="task-text" :class="{ completed: task.is_done }">
              {{ task.text }}
            </div>
            <input
              v-else
              v-model="editingText"
              @keyup.enter="saveEdit(task)"
              @keyup.escape="cancelEdit"
              @blur="saveEdit(task)"
              type="text"
              class="edit-input"
              ref="editInput"
            />
          </div>
          
          <!-- Task actions -->
          <div class="task-actions">
            <button
              v-if="editingTaskId !== task.id"
              @click="startEdit(task)"
              class="edit-btn"
              title="Edit task"
            >
              Edit
            </button>
            <button
              v-if="editingTaskId === task.id"
              @click="saveEdit(task)"
              class="save-btn"
              title="Save changes"
            >
              Save
            </button>
            <button
              v-if="editingTaskId === task.id"
              @click="cancelEdit"
              class="cancel-btn"
              title="Cancel editing"
            >
              Cancel
            </button>
            <button
              @click="deleteTask(task)"
              class="delete-btn"
              title="Delete task"
            >
              Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div v-if="tasks.length > 0" class="stats">
        <span>Total: {{ tasks.length }}</span>
        <span>Completed: {{ completedTasks }}</span>
        <span>Remaining: {{ remainingTasks }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick } from 'vue'

const API_BASE_URL = 'http://localhost:8000/api/v1'

export default {
  name: 'Todo',
  setup() {
    const tasks = ref([])
    const newTaskText = ref('')
    const loading = ref(false)
    const error = ref('')
    const editingTaskId = ref(null)
    const editingText = ref('')

    // Computed properties
    const completedTasks = computed(() => tasks.value.filter(task => task.is_done).length)
    const remainingTasks = computed(() => tasks.value.filter(task => !task.is_done).length)

    // API functions
    const apiCall = async (url, options = {}) => {
      try {
        const response = await fetch(`${API_BASE_URL}${url}`, {
          headers: {
            'Content-Type': 'application/json',
            ...options.headers
          },
          ...options
        })
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
        return await response.json()
      } catch (err) {
        console.error('API Error:', err)
        throw err
      }
    }

    const fetchTasks = async () => {
      loading.value = true
      error.value = ''
      try {
        const data = await apiCall('/tasks/')
        tasks.value = data
      } catch (err) {
        error.value = `Failed to fetch tasks: ${err.message}`
      } finally {
        loading.value = false
      }
    }

    const addTask = async () => {
      if (!newTaskText.value.trim()) return
      
      loading.value = true
      error.value = ''
      try {
        const newTask = await apiCall('/tasks/create/', {
          method: 'POST',
          body: JSON.stringify({ text: newTaskText.value.trim() })
        })
        tasks.value.push(newTask)
        newTaskText.value = ''
      } catch (err) {
        error.value = `Failed to add task: ${err.message}`
      } finally {
        loading.value = false
      }
    }

    const toggleTask = async (task) => {
      try {
        const updatedTask = await apiCall(`/tasks/${task.id}/update/`, {
          method: 'PATCH',
          body: JSON.stringify({ is_done: !task.is_done })
        })
        
        const index = tasks.value.findIndex(t => t.id === task.id)
        if (index !== -1) {
          tasks.value[index] = updatedTask
        }
      } catch (err) {
        error.value = `Failed to update task: ${err.message}`
      }
    }

    const startEdit = async (task) => {
      editingTaskId.value = task.id
      editingText.value = task.text
      
      await nextTick()
      // Focus the edit input
      const editInputs = document.querySelectorAll('.edit-input')
      editInputs.forEach(input => input.focus())
    }

    const saveEdit = async (task) => {
      if (!editingText.value.trim()) {
        cancelEdit()
        return
      }

      try {
        const updatedTask = await apiCall(`/tasks/${task.id}/update/`, {
          method: 'PATCH',
          body: JSON.stringify({ text: editingText.value.trim() })
        })
        
        const index = tasks.value.findIndex(t => t.id === task.id)
        if (index !== -1) {
          tasks.value[index] = updatedTask
        }
        
        editingTaskId.value = null
        editingText.value = ''
      } catch (err) {
        error.value = `Failed to update task: ${err.message}`
      }
    }

    const cancelEdit = () => {
      editingTaskId.value = null
      editingText.value = ''
    }

    const deleteTask = async (task) => {
      if (!confirm(`Are you sure you want to delete "${task.text}"?`)) return
      
      try {
        await apiCall(`/tasks/${task.id}/delete/`, {
          method: 'DELETE'
        })
        
        tasks.value = tasks.value.filter(t => t.id !== task.id)
      } catch (err) {
        error.value = `Failed to delete task: ${err.message}`
      }
    }

    // Lifecycle
    onMounted(() => {
      fetchTasks()
    })

    return {
      tasks,
      newTaskText,
      loading,
      error,
      editingTaskId,
      editingText,
      completedTasks,
      remainingTasks,
      addTask,
      toggleTask,
      startEdit,
      saveEdit,
      cancelEdit,
      deleteTask
    }
  }
}
</script>

<style scoped>
.todo-app {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.title {
  text-align: center;
  margin-bottom: 20px;
}

.input-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.task-input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ccc;
}

.add-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

.add-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error {
  background: #dc3545;
  color: white;
  padding: 10px;
  margin-bottom: 10px;
}

.no-tasks {
  text-align: center;
  color: #666;
  padding: 20px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #ddd;
  margin-bottom: 5px;
}

.task-content {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 10px;
}

.task-text.completed {
  text-decoration: line-through;
  color: #666;
}

.edit-input {
  flex: 1;
  padding: 4px;
  border: 1px solid #007bff;
}

.task-actions {
  display: flex;
  gap: 5px;
  margin-left: 6px;
}

.task-actions button {
  background: none;
  border: 1px solid #ccc;
  cursor: pointer;
  padding: 4px 8px;
}

.stats {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 10px;
  background: #f5f5f5;
}
</style>
