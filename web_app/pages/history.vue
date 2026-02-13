<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-400 rounded-lg shadow-lg p-6 text-white">
      <h1 class="text-3xl font-bold mb-2">✏️ แก้ไขประวัติการเช็คชื่อ</h1>
      <p class="text-blue-100">จัดการและแก้ไขข้อมูลการเช็คชื่อย้อนหลัง</p>
    </div>

    <!-- Date and Filter Section -->
    <div class="bg-white rounded-lg shadow-lg p-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Date Selector -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">เลือกวันที่:</label>
          <div class="flex space-x-2">
            <input 
              type="date" 
              v-model="selectedDate"
              @change="loadRecords"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button 
              @click="setToday"
              class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
            >
              วันนี้
            </button>
          </div>
        </div>

        <!-- Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">กรองตาม:</label>
          <select 
            v-model="filterType"
            @change="applyFilter"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">ทั้งหมด</option>
            <option value="camera">เช็คจากกล้อง</option>
            <option value="manual">เช็คด้วยมือ</option>
          </select>
        </div>

        <!-- Search -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">ค้นหาชื่อ:</label>
          <div class="relative">
            <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size="16" />
            <input 
              type="text"
              v-model="searchQuery"
              @input="applyFilter"
              placeholder="ค้นหาชื่อนักเรียน..."
              class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-200">
          <p class="text-sm text-blue-600 font-medium">รายการทั้งหมด</p>
          <p class="text-2xl font-bold text-blue-700">{{ filteredRecords.length }}</p>
        </div>
        <div class="bg-green-50 rounded-lg p-4 text-center border border-green-200">
          <p class="text-sm text-green-600 font-medium">เช็คจากกล้อง</p>
          <p class="text-2xl font-bold text-green-700">{{ cameraRecords }}</p>
        </div>
        <div class="bg-purple-50 rounded-lg p-4 text-center border border-purple-200">
          <p class="text-sm text-purple-600 font-medium">เช็คด้วยมือ</p>
          <p class="text-2xl font-bold text-purple-700">{{ manualRecords }}</p>
        </div>
        <div class="bg-orange-50 rounded-lg p-4 text-center border border-orange-200">
          <p class="text-sm text-orange-600 font-medium">กำลังแก้ไข</p>
          <p class="text-2xl font-bold text-orange-700">{{ editingCount }}</p>
        </div>
      </div>
    </div>

    <!-- Records Table -->
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
      <div class="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 class="text-lg font-bold text-blue-900 flex items-center">
          <FileText class="mr-2" size="20" />
          รายการเช็คชื่อ - {{ formatDate(selectedDate) }}
        </h2>
        <div class="flex items-center space-x-2">
          <button 
            @click="loadRecords"
            class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="รีเฟรช"
          >
            <RefreshCw size="20" :class="{ 'animate-spin': loading }" />
          </button>
          <button 
            @click="showBulkActions = !showBulkActions"
            class="px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm"
          >
            จัดการหลายรายการ
          </button>
        </div>
      </div>

      <!-- Bulk Actions -->
      <div v-if="showBulkActions" class="p-4 bg-gray-50 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <label class="flex items-center">
              <input 
                type="checkbox" 
                @change="toggleSelectAll"
                :checked="selectedRecords.length === filteredRecords.length && filteredRecords.length > 0"
                class="mr-2"
              />
              <span class="text-sm font-medium">เลือกทั้งหมด</span>
            </label>
            <span class="text-sm text-gray-600">เลือกแล้ว {{ selectedRecords.length }} รายการ</span>
          </div>
          <div class="flex items-center space-x-2">
            <button 
              @click="bulkDelete"
              :disabled="selectedRecords.length === 0"
              class="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 disabled:opacity-50 transition-colors text-sm"
            >
              ลบที่เลือก
            </button>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th v-if="showBulkActions" class="px-4 py-3 text-center">
                <input type="checkbox" class="opacity-0" />
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ชื่อ</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">เวลา</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ความมั่นใจ</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">แหล่งที่มา</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">จัดการ</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="record in paginatedRecords" :key="record.id" 
                class="hover:bg-gray-50 transition-colors"
                :class="{ 'bg-yellow-50': editingRecords.has(record.id) }">
              <!-- Bulk Select -->
              <td v-if="showBulkActions" class="px-4 py-3 text-center">
                <input 
                  type="checkbox" 
                  :value="record.id"
                  v-model="selectedRecords"
                  class="rounded"
                />
              </td>
              
              <!-- ID -->
              <td class="px-4 py-3 text-sm text-gray-500 font-mono">{{ record.id }}</td>
              
              <!-- Name -->
              <td class="px-4 py-3">
                <div v-if="editingRecords.has(record.id)">
                  <select 
                    v-model="editForms[record.id].name"
                    class="w-full px-2 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option v-for="student in modelStudents" :key="student.name" :value="student.name">
                      {{ student.name }}
                    </option>
                  </select>
                </div>
                <div v-else class="flex items-center">
                  <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold mr-3">
                    {{ record.name?.charAt(0).toUpperCase() }}
                  </div>
                  <span class="font-medium">{{ record.name }}</span>
                </div>
              </td>
              
              <!-- Time -->
              <td class="px-4 py-3 text-sm">
                <div v-if="editingRecords.has(record.id)">
                  <input 
                    type="time"
                    v-model="editForms[record.id].time"
                    class="px-2 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div v-else class="flex flex-col">
                  <span class="font-medium">{{ formatTime(record.timestamp) }}</span>
                  <span class="text-xs text-gray-500">{{ formatDate(record.timestamp) }}</span>
                </div>
              </td>
              
              <!-- Confidence -->
              <td class="px-4 py-3 text-sm">
                <span v-if="record.confidence_score" 
                      class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="getConfidenceClass(record.confidence_score)">
                  {{ (record.confidence_score * 100).toFixed(0) }}%
                </span>
                <span v-else class="text-gray-400">-</span>
              </td>
              
              <!-- Source -->
              <td class="px-4 py-3 text-sm">
                <span class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="record.camera_id === 'manual' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'">
                  {{ record.camera_id === 'manual' ? '✋ Manual' : '📷 Camera' }}
                </span>
              </td>
              
              <!-- Actions -->
              <td class="px-4 py-3 text-center">
                <div v-if="editingRecords.has(record.id)" class="flex items-center justify-center space-x-1">
                  <button 
                    @click="saveEdit(record.id)"
                    :disabled="savingRecords.has(record.id)"
                    class="p-2 bg-green-100 text-green-600 rounded-lg hover:bg-green-200 transition-colors"
                    title="บันทึก"
                  >
                    <Check size="16" />
                  </button>
                  <button 
                    @click="cancelEdit(record.id)"
                    class="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                    title="ยกเลิก"
                  >
                    <X size="16" />
                  </button>
                </div>
                <div v-else class="flex items-center justify-center space-x-1">
                  <button 
                    @click="startEdit(record)"
                    class="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
                    title="แก้ไข"
                  >
                    <Pencil size="16" />
                  </button>
                  <button 
                    @click="confirmDelete(record)"
                    class="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                    title="ลบ"
                  >
                    <Trash2 size="16" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="p-4 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-600">
          แสดง {{ (currentPage - 1) * itemsPerPage + 1 }} - {{ Math.min(currentPage * itemsPerPage, filteredRecords.length) }} 
          จาก {{ filteredRecords.length }} รายการ
        </div>
        <div class="flex items-center space-x-2">
          <button 
            @click="currentPage = Math.max(1, currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
          >
            ก่อนหน้า
          </button>
          <span class="px-3 py-2 bg-blue-100 text-blue-700 rounded-lg font-medium">
            {{ currentPage }} / {{ totalPages }}
          </span>
          <button 
            @click="currentPage = Math.min(totalPages, currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
          >
            ถัดไป
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredRecords.length === 0 && !loading" class="p-8 text-center text-gray-500">
        <FileText size="48" class="mx-auto mb-2 opacity-50" />
        <p>ไม่พบข้อมูลการเช็คชื่อในวันที่เลือก</p>
        <p class="text-sm mt-1">ลองเปลี่ยนวันที่หรือเงื่อนไขการกรอง</p>
      </div>
    </div>

    <!-- Add New Record -->
    <div class="bg-white rounded-lg shadow-lg p-6">
      <h2 class="text-lg font-bold text-blue-900 mb-4 flex items-center">
        <Plus class="mr-2" size="20" />
        เพิ่มรายการใหม่
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ชื่อนักเรียน</label>
          <select 
            v-model="newRecord.name"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- เลือกนักเรียน --</option>
            <option v-for="student in modelStudents" :key="student.name" :value="student.name">
              {{ student.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">วันที่</label>
          <input 
            type="date"
            v-model="newRecord.date"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">เวลา</label>
          <input 
            type="time"
            v-model="newRecord.time"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div class="flex items-end">
          <button 
            @click="addNewRecord"
            :disabled="!newRecord.name || adding"
            class="w-full py-2 bg-green-500 text-white font-medium rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="adding" class="flex items-center justify-center">
              <RefreshCw class="animate-spin mr-1" size="16" />
              กำลังเพิ่ม...
            </span>
            <span v-else class="flex items-center justify-center">
              <Plus class="mr-1" size="16" />
              เพิ่มรายการ
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-bold text-red-600 mb-4 flex items-center">
          <AlertTriangle class="mr-2" size="24" />
          ยืนยันการลบ
        </h3>
        <p class="text-gray-600 mb-6">
          <span v-if="deleteTarget">
            คุณต้องการลบรายการเช็คชื่อของ <strong>{{ deleteTarget.name }}</strong> หรือไม่?
          </span>
          <span v-else-if="selectedRecords.length > 0">
            คุณต้องการลบรายการที่เลือก <strong>{{ selectedRecords.length }}</strong> รายการหรือไม่?
          </span>
        </p>
        <div class="flex space-x-4">
          <button 
            @click="showDeleteModal = false; deleteTarget = null"
            class="flex-1 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            ยกเลิก
          </button>
          <button 
            @click="executeDelete"
            :disabled="deleting"
            class="flex-1 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 transition-colors"
          >
            {{ deleting ? 'กำลังลบ...' : 'ลบ' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" 
         class="fixed bottom-4 right-4 px-6 py-4 rounded-lg shadow-lg text-white z-50"
         :class="messageType === 'success' ? 'bg-green-500' : 'bg-red-500'">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { FileText, RefreshCw, Pencil, Trash2, Check, X, Plus, AlertTriangle, Search } from 'lucide-vue-next'

const config = useRuntimeConfig()

// State
const selectedDate = ref(new Date().toISOString().split('T')[0])
const records = ref([])
const filteredRecords = ref([])
const modelStudents = ref([])
const loading = ref(false)
const adding = ref(false)
const deleting = ref(false)
const message = ref('')
const messageType = ref('success')

// Edit state
const editingRecords = ref(new Set())
const savingRecords = ref(new Set())
const editForms = ref({})

// Filter and search
const filterType = ref('all')
const searchQuery = ref('')

// Bulk actions
const showBulkActions = ref(false)
const selectedRecords = ref([])

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(20)

// Modal state
const showDeleteModal = ref(false)
const deleteTarget = ref(null)

// New record
const newRecord = ref({
  name: '',
  date: new Date().toISOString().split('T')[0],
  time: '09:00'
})

// Computed
const cameraRecords = computed(() => records.value.filter(r => r.camera_id !== 'manual').length)
const manualRecords = computed(() => records.value.filter(r => r.camera_id === 'manual').length)
const editingCount = computed(() => editingRecords.value.size)

const totalPages = computed(() => Math.ceil(filteredRecords.value.length / itemsPerPage.value))

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredRecords.value.slice(start, end)
})

// Methods
const setToday = () => {
  selectedDate.value = new Date().toISOString().split('T')[0]
  loadRecords()
}

const loadRecords = async () => {
  loading.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/api/v1/attendance/by-date/${selectedDate.value}`)
    if (response.success) {
      records.value = response.data
      applyFilter()
    }
  } catch (error) {
    console.error('Error loading records:', error)
    showMessage('ไม่สามารถโหลดข้อมูลได้', 'error')
  } finally {
    loading.value = false
  }
}

const loadModelStudents = async () => {
  try {
    const response = await $fetch(`${config.public.apiBase}/api/v1/model/students`)
    if (response.success) {
      modelStudents.value = response.data
    }
  } catch (error) {
    console.error('Error loading model students:', error)
  }
}

const applyFilter = () => {
  let filtered = [...records.value]
  
  // Apply type filter
  if (filterType.value === 'camera') {
    filtered = filtered.filter(r => r.camera_id !== 'manual')
  } else if (filterType.value === 'manual') {
    filtered = filtered.filter(r => r.camera_id === 'manual')
  }
  
  // Apply search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(r => 
      r.name?.toLowerCase().includes(query)
    )
  }
  
  filteredRecords.value = filtered
  currentPage.value = 1
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('th-TH', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
}

const getConfidenceClass = (score) => {
  if (!score) return 'bg-gray-100 text-gray-600'
  if (score >= 0.9) return 'bg-green-100 text-green-700'
  if (score >= 0.7) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}

const startEdit = (record) => {
  editingRecords.value.add(record.id)
  editForms.value[record.id] = {
    name: record.name,
    time: formatTime(record.timestamp)
  }
}

const cancelEdit = (recordId) => {
  editingRecords.value.delete(recordId)
  delete editForms.value[recordId]
}

const saveEdit = async (recordId) => {
  savingRecords.value.add(recordId)
  try {
    const form = editForms.value[recordId]
    const timestamp = `${selectedDate.value}T${form.time}:00`
    
    const response = await $fetch(`${config.public.apiBase}/api/v1/attendance/${recordId}`, {
      method: 'PUT',
      body: {
        name: form.name,
        timestamp: timestamp
      }
    })
    
    if (response.success) {
      showMessage('บันทึกการแก้ไขสำเร็จ', 'success')
      cancelEdit(recordId)
      await loadRecords()
    }
  } catch (error) {
    console.error('Error saving edit:', error)
    showMessage('ไม่สามารถบันทึกได้', 'error')
  } finally {
    savingRecords.value.delete(recordId)
  }
}

const confirmDelete = (record) => {
  deleteTarget.value = record
  showDeleteModal.value = true
}

const bulkDelete = () => {
  if (selectedRecords.value.length === 0) return
  deleteTarget.value = null
  showDeleteModal.value = true
}

const executeDelete = async () => {
  deleting.value = true
  try {
    if (deleteTarget.value) {
      // Single delete
      const response = await $fetch(`${config.public.apiBase}/api/v1/attendance/${deleteTarget.value.id}`, {
        method: 'DELETE'
      })
      if (response.success) {
        showMessage('ลบรายการสำเร็จ', 'success')
      }
    } else if (selectedRecords.value.length > 0) {
      // Bulk delete
      const promises = selectedRecords.value.map(id => 
        $fetch(`${config.public.apiBase}/api/v1/attendance/${id}`, { method: 'DELETE' })
      )
      await Promise.all(promises)
      showMessage(`ลบ ${selectedRecords.value.length} รายการสำเร็จ`, 'success')
      selectedRecords.value = []
    }
    
    showDeleteModal.value = false
    deleteTarget.value = null
    await loadRecords()
  } catch (error) {
    console.error('Error deleting record:', error)
    showMessage('ไม่สามารถลบได้', 'error')
  } finally {
    deleting.value = false
  }
}

const toggleSelectAll = () => {
  if (selectedRecords.value.length === filteredRecords.value.length) {
    selectedRecords.value = []
  } else {
    selectedRecords.value = filteredRecords.value.map(r => r.id)
  }
}

const addNewRecord = async () => {
  if (!newRecord.value.name) return
  
  adding.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/api/v1/attendance/manual-save`, {
      method: 'POST',
      body: {
        date: newRecord.value.date,
        students: [{ name: newRecord.value.name, present: true }]
      }
    })
    
    if (response.success) {
      showMessage('เพิ่มรายการสำเร็จ', 'success')
      newRecord.value = {
        name: '',
        date: new Date().toISOString().split('T')[0],
        time: '09:00'
      }
      await loadRecords()
    }
  } catch (error) {
    console.error('Error adding record:', error)
    showMessage('ไม่สามารถเพิ่มได้', 'error')
  } finally {
    adding.value = false
  }
}

const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

// Lifecycle
onMounted(() => {
  loadRecords()
  loadModelStudents()
})

// Watch for filter changes
watch([filterType, searchQuery], () => {
  applyFilter()
})
</script>
