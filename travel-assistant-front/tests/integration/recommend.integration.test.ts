import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { setupServer } from 'msw/node'
import { HttpResponse, http } from 'msw'
import { useRecommend } from '@/hooks/useRecommend'
import { agentApiService } from '@/services/agentApi'

// Mock recommend component for testing
type RecommendComponentProps = {
  onRecommend: (params: any) => Promise<void>
  loading: boolean
  error: any
  results: any
}

const RecommendComponent = ({ onRecommend, loading, error, results }: RecommendComponentProps) => {
  return (
    <div>
      <h2>Get Travel Recommendations</h2>
      <div>
        <label>Destination:</label>
        <input data-testid="destination-input" defaultValue="Tokyo" />
      </div>
      <div>
        <label>Start Date:</label>
        <input data-testid="start-date-input" defaultValue="2025-02-01" />
      </div>
      <div>
        <label>End Date:</label>
        <input data-testid="end-date-input" defaultValue="2025-02-14" />
      </div>
      <div>
        <label>Preferences:</label>
        <select data-testid="preferences-input" multiple>
          <option value="culture">Culture</option>
          <option value="food">Food</option>
          <option value="nature">Nature</option>
        </select>
      </div>
      <button data-testid="recommend-button" onClick={() => {
        const destination = (document.querySelector('[data-testid="destination-input"]') as HTMLInputElement).value
        const startDate = (document.querySelector('[data-testid="start-date-input"]') as HTMLInputElement).value
        const endDate = (document.querySelector('[data-testid="end-date-input"]') as HTMLInputElement).value
        const preferencesSelect = document.querySelector('[data-testid="preferences-input"]') as HTMLSelectElement
        const preferences = Array.from(preferencesSelect.selectedOptions).map(option => option.value)
        
        onRecommend({ destination, start_date: startDate, end_date: endDate, preferences })
      }} disabled={loading}>
        {loading ? 'Getting Recommendations...' : 'Get Recommendations'}
      </button>
      
      {error && <div data-testid="error-message" className="error">{error.message}</div>}
      
      {results && (
        <div data-testid="recommend-results">
          <h3>Recommendations for {results.destination_info?.destination}</h3>
          <p>Found {results.attractions?.length || 0} attractions</p>
          <p>Weather forecast: {results.weather_forecast?.length || 0} days</p>
        </div>
      )}
    </div>
  )
}

// Create mock server
const server = setupServer()

// Mock data
const mockRecommendResponse = {
  success: true,
  task_id: 'test-recommend-task-id-456',
  destination_info: {
    destination: 'Tokyo',
    country: 'Japan',
    best_time_to_visit: 'Spring and Autumn',
    currency: 'JPY'
  },
  attractions: [
    {
      name: 'Shibuya Crossing',
      category: 'Landmark',
      rating: 4.8,
      description: 'Famous pedestrian crossing'
    },
    {
      name: 'Senso-ji Temple',
      category: 'Temple',
      rating: 4.7,
      description: 'Ancient Buddhist temple'
    }
  ],
  weather_forecast: [
    {
      date: '2025-02-01',
      condition: 'Sunny',
      temperature_high: 12,
      temperature_low: 5
    },
    {
      date: '2025-02-02',
      condition: 'Partly Cloudy',
      temperature_high: 11,
      temperature_low: 4
    }
  ],
  reviews: {
    overall_rating: 4.6,
    total_reviews: 1250,
    recommended_by: 92
  }
}

describe('Recommend Integration Tests', () => {
  beforeEach(() => {
    // Start mock server before each test
    server.listen()
  })

  afterEach(() => {
    // Reset and close mock server after each test
    server.resetHandlers()
    server.close()
  })

  it('should render recommend component and handle user input', async () => {
    const mockOnRecommend = vi.fn()
    
    render(
      <RecommendComponent 
        onRecommend={mockOnRecommend}
        loading={false}
        error={null}
        results={null}
      />
    )

    // Verify component renders correctly
    expect(screen.getByText('Get Travel Recommendations')).toBeInTheDocument()
    expect(screen.getByTestId('destination-input')).toHaveValue('Tokyo')
    expect(screen.getByTestId('recommend-button')).toBeInTheDocument()
  })

  it('should handle recommend button click and call onRecommend', async () => {
    const mockOnRecommend = vi.fn()
    
    render(
      <RecommendComponent 
        onRecommend={mockOnRecommend}
        loading={false}
        error={null}
        results={null}
      />
    )

    const recommendButton = screen.getByTestId('recommend-button')
    await userEvent.click(recommendButton)

    expect(mockOnRecommend).toHaveBeenCalledWith({
      destination: 'Tokyo',
      start_date: '2025-02-01',
      end_date: '2025-02-14',
      preferences: []
    })
  })

  it('should show loading state during recommendation', async () => {
    const mockOnRecommend = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
    
    const { rerender } = render(
      <RecommendComponent 
        onRecommend={mockOnRecommend}
        loading={false}
        error={null}
        results={null}
      />
    )

    const recommendButton = screen.getByTestId('recommend-button')
    await userEvent.click(recommendButton)

    // Update to loading state
    rerender(
      <RecommendComponent 
        onRecommend={mockOnRecommend}
        loading={true}
        error={null}
        results={null}
      />
    )

    expect(screen.getByTestId('recommend-button')).toHaveTextContent('Getting Recommendations...')
    expect(screen.getByTestId('recommend-button')).toBeDisabled()
  })

  it('should display recommendation results after successful request', async () => {
    const mockOnRecommend = vi.fn().mockResolvedValue(mockRecommendResponse)
    
    const { rerender } = render(
      <RecommendComponent 
        onRecommend={mockOnRecommend}
        loading={false}
        error={null}
        results={null}
      />
    )

    const recommendButton = screen.getByTestId('recommend-button')
    await userEvent.click(recommendButton)

    // Update to show results
    rerender(
      <RecommendComponent 
        onRecommend={mockOnRecommend}
        loading={false}
        error={null}
        results={mockRecommendResponse}
      />
    )

    expect(screen.getByTestId('recommend-results')).toBeInTheDocument()
    expect(screen.getByText('Recommendations for Tokyo')).toBeInTheDocument()
    expect(screen.getByText('Found 2 attractions')).toBeInTheDocument()
    expect(screen.getByText('Weather forecast: 2 days')).toBeInTheDocument()
  })

  it('should display error message when recommendation fails', async () => {
    const mockError = new Error('Recommendation failed')
    const mockOnRecommend = vi.fn().mockRejectedValue(mockError)
    
    const { rerender } = render(
      <RecommendComponent 
        onRecommend={mockOnRecommend}
        loading={false}
        error={null}
        results={null}
      />
    )

    const recommendButton = screen.getByTestId('recommend-button')
    await userEvent.click(recommendButton)

    // Update to show error
    rerender(
      <RecommendComponent 
        onRecommend={mockOnRecommend}
        loading={false}
        error={mockError}
        results={null}
      />
    )

    expect(screen.getByTestId('error-message')).toBeInTheDocument()
    expect(screen.getByText('Recommendation failed')).toBeInTheDocument()
  })

  it('should handle API mocking with MSW', async () => {
    // Setup mock handler
    server.use(
      http.post('http://localhost:8000/api/agent/recommend', () => {
        return HttpResponse.json(mockRecommendResponse)
      })
    )

    // Mock the agentApiService.recommend method
    const originalRecommend = agentApiService.recommend
    agentApiService.recommend = vi.fn().mockImplementation(async (params) => {
      const response = await fetch('http://localhost:8000/api/agent/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      })
      return response.json()
    })

    const { recommend } = useRecommend()
    
    // Test the recommend function
    const recommendParams = {
      destination: 'Tokyo',
      start_date: '2025-02-01',
      end_date: '2025-02-14',
      preferences: ['culture', 'food']
    }

    const result = await recommend(recommendParams)
    
    expect(result).toEqual(mockRecommendResponse)
    expect(agentApiService.recommend).toHaveBeenCalledWith(recommendParams)

    // Restore original method
    agentApiService.recommend = originalRecommend
  })

  it('should handle user input changes for preferences', async () => {
    const mockOnRecommend = vi.fn()
    
    render(
      <RecommendComponent 
        onRecommend={mockOnRecommend}
        loading={false}
        error={null}
        results={null}
      />
    )

    const preferencesSelect = screen.getByTestId('preferences-input')
    const destinationInput = screen.getByTestId('destination-input')

    // Select multiple preferences
    await userEvent.selectOptions(preferencesSelect, ['culture', 'food'])
    await userEvent.clear(destinationInput)
    await userEvent.type(destinationInput, 'Osaka')

    const recommendButton = screen.getByTestId('recommend-button')
    await userEvent.click(recommendButton)

    expect(mockOnRecommend).toHaveBeenCalledWith({
      destination: 'Osaka',
      start_date: '2025-02-01',
      end_date: '2025-02-14',
      preferences: ['culture', 'food']
    })
  })
})