<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-400 rounded-lg shadow-lg p-6 text-white">
      <h1 class="text-3xl font-bold mb-2">👥 รายชื่อนักเรียน</h1>
      <p class="text-blue-100">รายชื่อนักเรียนที่มีในโมเดลตรวจจับใบหน้า (label_map.json)</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow-lg p-4 border-l-4 border-blue-500">
        <p class="text-gray-600 text-sm">นักเรียนทั้งหมด</p>
        <p class="text-3xl font-bold text-blue-600">{{ modelStudents.length }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-lg p-4 border-l-4 border-green-500">
        <p class="text-gray-600 text-sm">มาเรียนวันนี้</p>
        <p class="text-3xl font-bold text-green-600">{{ todayPresentCount }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-lg p-4 border-l-4 border-red-500">
        <p class="text-gray-600 text-sm">ขาดเรียนวันนี้</p>
        <p class="text-3xl font-bold text-red-600">{{ modelStudents.length - todayPresentCount }}</p>
      </div>
    </div>

    <!-- Student List from Model -->
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
      <div class="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 class="text-lg font-bold text-blue-900 flex items-center">
          <Users class="mr-2" size="20" />
          รายชื่อจากโมเดล (label_map.json)
        </h2>
        <button 
          @click="loadData"
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="รีเฟรช"
        >
          <RefreshCw size="20" :class="{ 'animate-spin': loading }" />
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ชื่อ</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">สถานะวันนี้</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">จำนวนครั้งที่มา</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">ดูประวัติ</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="student in modelStudents" :key="student.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm text-gray-500">{{ student.id }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center">
                  <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold mr-3"
                       :class="getStudentStatus(student.name) ? 'bg-green-500' : 'bg-gray-400'">
                    {{ student.name.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">{{ student.name }}</p>
                    <p class="text-xs text-gray-500">จากโมเดลตรวจจับใบหน้า</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <span v-if="getStudentStatus(student.name)" 
                      class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                  ✓ มาเรียน
                </span>
                <span v-else 
                      class="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                  ✗ ยังไม่มา
                </span>
              </td>
              <td class="px-4 py-3 text-sm">
                <span class="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                  {{ getAttendanceCount(student.name) }} ครั้ง
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <button 
                  @click="viewStudentHistory(student.name)"
                  class="px-3 py-1 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors text-sm"
                >
                  ดูประวัติ
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="modelStudents.length === 0 && !loading" class="p-8 text-center text-gray-500">
        <Users size="48" class="mx-auto mb-2 opacity-50" />
        <p>ไม่พบข้อมูลนักเรียนในโมเดล</p>
        <p class="text-sm">กรุณาตรวจสอบไฟล์ model_store/label_map.json</p>
      </div>
    </div>

    <!-- Student History Modal -->
    <div v-if="showHistoryModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-blue-900">
            📋 ประวัติการเข้าเรียนของ {{ selectedStudent }}
          </h3>
          <button @click="showHistoryModal = false" class="p-2 hover:bg-gray-100 rounded-lg">
            <X size="20" />
          </button>
        </div>
        
        <div v-if="studentHistory.length > 0" class="space-y-2">
          <div v-for="record in studentHistory" :key="record.id"
               class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center">
              <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white mr-3">
                ✓
              </div>
              <div>
                <p class="font-medium">{{ formatDate(record.timestamp) }}</p>
                <p class="text-xs text-gray-500">{{ formatTime(record.timestamp) }}</p>
              </div>
            </div>
            <span class="text-xs px-2 py-1 rounded-full"
                  :class="record.camera_id === 'manual' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'">
              {{ record.camera_id === 'manual' ? '✋ Manual' : '📷 Camera' }}
            </span>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          <p>ไม่พบประวัติการเข้าเรียน</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Users, RefreshCw, X } from 'lucide-vue-next'

const config = useRuntimeConfig()

// State
const modelStudents = ref([])
const todayAttendance = ref([])
const allAttendance = ref([])
const loading = ref(false)
const showHistoryModal = ref(false)
const selectedStudent = ref('')
const studentHistory = ref([])

// Computed
const todayPresentCount = computed(() => {
  return todayAttendance.value.length
})

// Methods
const loadData = async () => {
  loading.value = true
  try {
    // Load model students
    const studentsRes = await $fetch(`${config.public.apiBase}/api/v1/model/students`)
    if (studentsRes.success) {
      modelStudents.value = studentsRes.data
    }
    
    // Load today's attendance
    const today = new Date().toISOString().split('T')[0]
    const todayRes = await $fetch(`${config.public.apiBase}/api/v1/attendance/by-date/${today}`)
    if (todayRes.success) {
      todayAttendance.value = todayRes.data
    }
    
    // Load all attendance for counts
    const allRes = await $fetch(`${config.public.apiBase}/api/v1/attendance/history?limit=1000`)
    if (allRes.success) {
      allAttendance.value = allRes.data
    }
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

const getStudentStatus = (name) => {
  return todayAttendance.value.some(a => a.name === name)
}

const getAttendanceCount = (name) => {
  return allAttendance.value.filter(a => a.name === name).length
}

const viewStudentHistory = async (name) => {
  selectedStudent.value = name
  studentHistory.value = allAttendance.value.filter(a => a.name === name)
  showHistoryModal.value = true
}

const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
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

// Lifecycle
onMounted(() => {
  loadData()
})
</script>
