<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const appointments = ref([])
const availabilities = ref([])
const currentView = ref('schedule')
const selectedApp = ref(null)
const treatmentData = ref({ diagnosis: '', prescription: '', notes: '' })
const editApp = ref(null)
const editTreatment = ref({ diagnosis: '', prescription: '', notes: '' })
const newSlot = ref({ date: '', start_time: '', end_time: '' })
const patientHistory = ref(null)
const statusMsg = ref({ text: '', type: '' })

const showMsg = (text, type = 'success') => {
    statusMsg.value = { text, type }
    setTimeout(() => { statusMsg.value = { text: '', type: '' } }, 3500)
}

const fetchAppointments = async () => {
    try {
        const response = await axios.get('/api/doctor/appointments')
        appointments.value = response.data
    } catch (err) {
        console.error('Failed to fetch appointments', err)
    }
}

const fetchAvailability = async () => {
    const res = await axios.get('/api/doctor/availability')
    availabilities.value = res.data
}

const addSlot = async () => {
    // Client-side validation
    if (!newSlot.value.date || !newSlot.value.start_time || !newSlot.value.end_time) {
        showMsg('Please fill in all fields', 'danger')
        return
    }
    if (newSlot.value.end_time <= newSlot.value.start_time) {
        showMsg('End time must be after start time', 'danger')
        return
    }
    const slotDT = new Date(`${newSlot.value.date}T${newSlot.value.start_time}`)
    if (slotDT <= new Date()) {
        showMsg('Cannot create a slot in the past', 'danger')
        return
    }
    try {
        await axios.post('/api/doctor/availability', newSlot.value)
        newSlot.value = { date: '', start_time: '', end_time: '' }
        fetchAvailability()
        showMsg('Slot added successfully')
    } catch (err) {
        showMsg(err.response?.data?.msg || 'Failed to add slot', 'danger')
    }
}

const deleteSlot = async (id) => {
    if (confirm('Are you sure you want to delete this available slot?')) {
        try {
            await axios.delete(`/api/doctor/availability/${id}`)
            fetchAvailability()
            showMsg('Slot deleted successfully')
        } catch (err) {
            showMsg(err.response?.data?.msg || 'Failed to delete slot', 'danger')
        }
    }
}

const viewHistory = async (patientId) => {
    try {
        const res = await axios.get(`/api/doctor/patient-history/${patientId}`)
        patientHistory.value = res.data
    } catch (err) {
        showMsg('Failed to fetch history', 'danger')
    }
}

onMounted(() => {
    fetchAppointments()
})

const setView = (view) => {
    currentView.value = view
    if (view === 'availability') fetchAvailability()
}

const openCompleteModal = (app) => {
    selectedApp.value = app
    treatmentData.value = { diagnosis: '', prescription: '', notes: '' }
}

const submitTreatment = async () => {
    try {
        await axios.post(`/api/doctor/appointments/${selectedApp.value.id}/complete`, treatmentData.value)
        showMsg('Treatment recorded successfully')
        await fetchAppointments()
    } catch (err) {
        showMsg('Failed to update appointment', 'danger')
    }
}

const cancelAppointment = async (id) => {
    if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
            await axios.post(`/api/doctor/appointments/${id}/cancel`)
            showMsg('Appointment cancelled successfully')
            await fetchAppointments()
        } catch (err) {
            showMsg(err.response?.data?.msg || 'Cancellation failed', 'danger')
        }
    }
}

const openEditTreatment = (app) => {
    editApp.value = app
    editTreatment.value = {
        diagnosis: app.diagnosis || '',
        prescription: app.prescription || '',
        notes: app.notes || ''
    }
}

const submitEditTreatment = async () => {
    try {
        await axios.put(`/api/doctor/appointments/${editApp.value.id}/treatment`, editTreatment.value)
        showMsg('Treatment record updated successfully')
        await fetchAppointments()
        editApp.value = null
    } catch (err) {
        showMsg(err.response?.data?.msg || 'Failed to update treatment', 'danger')
    }
}
</script>

<template>
  <div class="fade-in">
    <!-- Global Status Alert -->
    <div v-if="statusMsg.text" :class="['alert', 'alert-' + statusMsg.type, 'position-fixed', 'top-0', 'end-0', 'm-4', 'shadow-lg']" style="z-index: 9999;">
        {{ statusMsg.text }}
    </div>

    <div class="d-flex justify-content-between align-items-center mb-5">
        <div>
            <h2 class="fw-bold mb-1">Clinical Portfolio</h2>
            <p class="text-muted mb-0">Manage your daily schedule and patient consultation records</p>
        </div>
        <div class="bg-white p-1 rounded-3 shadow-sm border">
            <div class="btn-group border-0">
                <button class="btn btn-sm px-4" :class="currentView === 'schedule' ? 'btn-primary shadow-sm' : 'btn-light'" @click="setView('schedule')">Schedule</button>
                <button class="btn btn-sm px-4" :class="currentView === 'availability' ? 'btn-primary shadow-sm' : 'btn-light'" @click="setView('availability')">Availability</button>
            </div>
        </div>
    </div>

    <!-- Schedule View -->
    <div v-if="currentView === 'schedule'" class="card border-0 p-4 shadow-sm mb-4 fade-in">
      <div class="d-flex justify-content-between align-items-center mb-3">
          <h4 class="fw-bold mb-0">Appointments</h4>
          <span class="badge bg-primary-subtle text-primary border border-primary-subtle">{{ appointments.filter(a => a.status === 'Booked').length }} Pending</span>
      </div>
      
      <div v-if="appointments.length === 0" class="text-center py-5">
        <i class="bi bi-calendar-x text-muted fs-1 mb-2 d-block"></i>
        <p class="text-muted">No appointments scheduled for this period.</p>
      </div>
      
      <div v-else class="table-responsive">
        <table class="table hover align-middle">
          <thead>
            <tr>
              <th class="ps-3">Patient</th>
              <th>Date & Time</th>
              <th>Status</th>
              <th>Diagnosis</th>
              <th class="text-end pe-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in appointments" :key="app.id">
              <td class="ps-3">
                <div class="d-flex align-items-center">
                    <div class="d-flex align-items-center justify-content-center me-3 rounded-circle" style="width: 38px; height: 38px; background: #eef2ff; color: #4f46e5;">
                        <i class="bi bi-person"></i>
                    </div>
                    <span class="fw-bold">{{ app.patient }}</span>
                </div>
              </td>
              <td>
                  <span class="d-block fw-semibold">{{ app.date }}</span>
                  <small class="text-muted"><i class="bi bi-clock me-1"></i>{{ app.time }}</small>
              </td>
              <td>
                <span :class="['badge rounded-pill', app.status === 'Completed' ? 'bg-success-subtle text-success' : (app.status === 'Cancelled' ? 'bg-danger-subtle text-danger' : 'bg-primary-subtle text-primary')]">
                  {{ app.status }}
                </span>
              </td>
              <td>
                <span v-if="app.diagnosis" class="text-muted small">{{ app.diagnosis }}</span>
                <span v-else class="text-muted small opacity-50">—</span>
              </td>
              <td class="text-end pe-3">
                <div class="d-flex gap-2 justify-content-end">
                    <!-- Complete visit (only for Booked) -->
                    <button v-if="app.status === 'Booked'" class="btn btn-sm btn-primary shadow-sm px-3" data-bs-toggle="modal" data-bs-target="#completeModal" @click="openCompleteModal(app)">
                        Complete Visit
                    </button>
                    <button v-if="app.status === 'Booked'" class="btn btn-sm btn-outline-danger border-0 h-100" @click="cancelAppointment(app.id)" title="Cancel Appointment">
                        <i class="bi bi-x-circle me-1"></i>Cancel
                    </button>
                    <!-- Edit treatment (only for Completed) -->
                    <button v-if="app.status === 'Completed'" class="btn btn-sm btn-outline-warning border-0" data-bs-toggle="modal" data-bs-target="#editTreatmentModal" @click="openEditTreatment(app)" title="Edit Treatment Record">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <!-- View patient history (any status) -->
                    <button class="btn btn-sm btn-outline-secondary border-0" data-bs-toggle="modal" data-bs-target="#historyModal" @click="viewHistory(app.patient_id)" title="View Medical History">
                        <i class="bi bi-journal-medical"></i>
                    </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Availability View -->
    <div v-if="currentView === 'availability'" class="fade-in">
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card border-0 p-4 shadow-sm">
                    <h5 class="fw-bold mb-4">Add Time Slot</h5>
                    <form @submit.prevent="addSlot">
                        <div class="mb-3">
                            <label class="form-label small fw-semibold">Consultation Date</label>
                            <input v-model="newSlot.date" type="date" class="form-control bg-light border-0" required>
                        </div>
                        <div class="row g-2 mb-4">
                            <div class="col-6">
                                <label class="form-label small fw-semibold">Start Time</label>
                                <input v-model="newSlot.start_time" type="time" class="form-control bg-light border-0" required>
                            </div>
                            <div class="col-6">
                                <label class="form-label small fw-semibold">End Time</label>
                                <input v-model="newSlot.end_time" type="time" class="form-control bg-light border-0" required>
                            </div>
                        </div>
                        <button class="btn btn-primary w-100 py-2 shadow-sm fw-bold">Open Slot</button>
                    </form>
                </div>
            </div>
            <div class="col-md-8">
                <div class="card border-0 p-4 shadow-sm h-100">
                    <h5 class="fw-bold mb-4">My Availability</h5>
                    <div class="table-responsive">
                        <table class="table hover align-middle">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Timing Window</th>
                                    <th>Current Status</th>
                                    <th class="text-end pe-3">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="s in availabilities" :key="s.id">
                                    <td class="fw-bold">{{ s.date }}</td>
                                    <td>{{ s.start_time }} - {{ s.end_time }}</td>
                                    <td>
                                        <span :class="['badge rounded-pill', s.is_booked ? 'bg-info-subtle text-info' : 'bg-success-subtle text-success']">
                                            {{ s.is_booked ? 'Booked' : 'Available' }}
                                        </span>
                                    </td>
                                    <td class="text-end pe-3">
                                        <button v-if="!s.is_booked" class="btn btn-sm btn-outline-danger border-0" @click="deleteSlot(s.id)" title="Delete Slot">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                                <tr v-if="availabilities.length === 0">
                                    <td colspan="4" class="text-center py-5 text-muted">No availability slots defined.</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
  </div>

  <!-- Complete Appointment Modal -->
  <div class="modal fade" id="completeModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content border-0 shadow-lg">
              <div class="modal-header border-0 pb-0">
                  <h5 class="modal-title fw-bold">Consultation Report: {{ selectedApp?.patient }}</h5>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body">
                  <form @submit.prevent="submitTreatment">
                      <div class="mb-3">
                          <label class="form-label small fw-semibold">Final Diagnosis</label>
                          <input v-model="treatmentData.diagnosis" type="text" class="form-control bg-light border-0" placeholder="e.g. Acute Rhinitis" required>
                      </div>
                      <div class="mb-3">
                          <label class="form-label small fw-semibold">Prescribed medication</label>
                          <textarea v-model="treatmentData.prescription" class="form-control bg-light border-0" rows="3" placeholder="List medications and dosage..."></textarea>
                      </div>
                      <div class="mb-4">
                          <label class="form-label small fw-semibold">Consultation Notes (Private)</label>
                          <textarea v-model="treatmentData.notes" class="form-control bg-light border-0" rows="3" placeholder="Advice and follow-up plan..."></textarea>
                      </div>
                      <button type="submit" class="btn btn-success w-100 py-2 fw-bold shadow-sm" data-bs-dismiss="modal">Finalize & Complete Visit</button>
                  </form>
              </div>
          </div>
      </div>
  </div>

  <!-- Edit Treatment Modal -->
  <div class="modal fade" id="editTreatmentModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content border-0 shadow-lg">
              <div class="modal-header border-0 pb-0" style="background: #fffbeb;">
                  <div>
                      <h5 class="modal-title fw-bold"><i class="bi bi-pencil-square me-2 text-warning"></i>Edit Treatment Record</h5>
                      <p class="text-muted small mb-0 mt-1">Patient: {{ editApp?.patient }} — {{ editApp?.date }}</p>
                  </div>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body">
                  <form @submit.prevent="submitEditTreatment">
                      <div class="mb-3">
                          <label class="form-label small fw-semibold">Diagnosis</label>
                          <input v-model="editTreatment.diagnosis" type="text" class="form-control bg-light border-0" required>
                      </div>
                      <div class="mb-3">
                          <label class="form-label small fw-semibold">Prescription</label>
                          <textarea v-model="editTreatment.prescription" class="form-control bg-light border-0" rows="3"></textarea>
                      </div>
                      <div class="mb-4">
                          <label class="form-label small fw-semibold">Consultation Notes</label>
                          <textarea v-model="editTreatment.notes" class="form-control bg-light border-0" rows="3"></textarea>
                      </div>
                      <div class="d-flex gap-2">
                          <button type="button" class="btn btn-light flex-grow-1" data-bs-dismiss="modal">Cancel</button>
                          <button type="submit" class="btn btn-warning fw-bold flex-grow-1 shadow-sm" data-bs-dismiss="modal">
                              <i class="bi bi-check-circle me-2"></i>Save Changes
                          </button>
                      </div>
                  </form>
              </div>
          </div>
      </div>
  </div>

  <!-- Patient History Modal -->
  <div class="modal fade" id="historyModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content border-0 shadow-lg">
              <div class="modal-header bg-light border-0">
                  <h5 class="modal-title fw-bold">Clinical History: {{ patientHistory?.patient }}</h5>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body p-4">
                  <div v-if="!patientHistory?.history?.length" class="text-muted text-center py-5">
                      <i class="bi bi-file-earmark-text fs-1 d-block mb-3 opacity-25"></i>
                      No previous consultation records found.
                  </div>
                  <div v-else class="timeline">
                      <div v-for="h in patientHistory.history" :key="h.date" class="mb-4 position-relative ps-4 border-start border-2 border-primary-subtle">
                          <div class="position-absolute translate-middle-x" style="left: 0px; top: 0px;">
                              <div class="bg-primary rounded-circle" style="width: 12px; height: 12px; border: 3px solid white; box-shadow: 0 0 0 1px #4f46e5;"></div>
                          </div>
                          <div class="d-flex justify-content-between align-items-center mb-2">
                              <span class="fw-bold text-primary">{{ h.date }}</span>
                              <span class="badge bg-light text-dark border small fw-normal">Dr. {{ h.doctor }}</span>
                          </div>
                          <div class="card bg-light-subtle p-3 border-0 shadow-sm">
                              <p class="mb-2 fw-bold text-dark"><i class="bi bi-check2-circle text-success me-2"></i>{{ h.diagnosis }}</p>
                              <p class="mb-2 small text-muted"><strong>Prescription:</strong> {{ h.prescription }}</p>
                              <p class="mb-0 text-muted small italic" v-if="h.notes">Advisor: {{ h.notes }}</p>
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      </div>
  </div>
</template>
