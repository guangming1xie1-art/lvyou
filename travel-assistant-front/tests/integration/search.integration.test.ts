import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { setupServer } from 'msw/node'
import { HttpResponse, http } from 'msw'
import { useSearch } from '@/hooks/useSearch'
import { agentApiService } from '@/services/agentApi'

// Mock search component for testing
type SearchComponentProps = {
  onSearch: (params: any) => Promise<void>
  loading: boolean
  error: any
  results: any
}

const SearchComponent = ({ onSearch, loading, error, results }: SearchComponentProps) => {
  return (
    <div>
      <h2>Search Travel</h2>
      <div>
        <label>Origin:</label>
        <input data-testid="origin-input" defaultValue="Beijing" />
      </div>
      <div>
        <label>Destination:</label>
        <input data-testid="destination-input" defaultValue="Tokyo" />
      </div>
      <div>
        <label>Departure Date:</label>
        <input data-testid="departure-date-input" defaultValue="2025-02-01" />
      </div>
      <div>
        <label>Passengers:</label>
        <input data-testid="passengers-input" defaultValue="2" />
      </div>
      <button data-testid="search-button" onClick={() => {
        const origin = (document.querySelector('[data-testid="origin-input"]') as HTMLInputElement).value
        const destination = (document.querySelector('[data-testid="destination-input"]') as HTMLInputElement).value
        const departureDate = (document.querySelector('[data-testid="departure-date-input"]') as HTMLInputElement).value
        const passengers = parseInt((document.querySelector('[data-testid="passengers-input"]') as HTMLInputElement).value)
        
        onSearch({ origin, destination, departure_date: departureDate, passengers })
      }} disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
      
      {error && <div data-testid="error-message" className="error">{error.message}</div>}
      
      {results && (
        <div data-testid="search-results">
          <h3>Search Results</h3>
          <p>Found {results.outbound_flights?.length || 0} flights and {results.hotels?.length || 0} hotels</p>
        </div>
      )}
    </div>
  )
}

// Create mock server
const server = setupServer()

// Mock data
const mockSearchResponse = {
  success: true,
  task_id: 'test-task-id-123',
  outbound_flights: [
    {
      flight_id: 'FL123',
      airline: 'Sample Airline',
      flight_number: 'SA123',
      departure_time: '2025-02-01T08:00:00',
      arrival_time: '2025-02-01T12:00:00',
      total_price: 800.0,
      currency: 'USD'
    }
  ],
  hotels: [
    {
      hotel_id: 'HT456',
      name: 'Sample Hotel',
      rating: 4.5,
      price_per_night: 200.0
    }
  ]
}

describe('Search Integration Tests', () => {
  beforeEach(() => {
    // Start mock server before each test
    server.listen()
  })

  afterEach(() => {
    // Reset and close mock server after each test
    server.resetHandlers()
    server.close()
  })

  it('should render search component and handle user input', async () => {
    const mockOnSearch = vi.fn()
    
    render(
      <SearchComponent 
        onSearch={mockOnSearch}
        loading={false}
        error={null}
        results={null}
      />
    )

    // Verify component renders correctly
    expect(screen.getByText('Search Travel')).toBeInTheDocument()
    expect(screen.getByTestId('origin-input')).toHaveValue('Beijing')
    expect(screen.getByTestId('destination-input')).toHaveValue('Tokyo')
    expect(screen.getByTestId('search-button')).toBeInTheDocument()
  })

  it('should handle search button click and call onSearch', async () => {
    const mockOnSearch = vi.fn()
    
    render(
      <SearchComponent 
        onSearch={mockOnSearch}
        loading={false}
        error={null}
        results={null}
      />
    )

    const searchButton = screen.getByTestId('search-button')
    await userEvent.click(searchButton)

    expect(mockOnSearch).toHaveBeenCalledWith({
      origin: 'Beijing',
      destination: 'Tokyo',
      departure_date: '2025-02-01',
      passengers: 2
    })
  })

  it('should show loading state during search', async () => {
    const mockOnSearch = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
    
    const { rerender } = render(
      <SearchComponent 
        onSearch={mockOnSearch}
        loading={false}
        error={null}
        results={null}
      />
    )

    const searchButton = screen.getByTestId('search-button')
    await userEvent.click(searchButton)

    // Update to loading state
    rerender(
      <SearchComponent 
        onSearch={mockOnSearch}
        loading={true}
        error={null}
        results={null}
      />
    )

    expect(screen.getByTestId('search-button')).toHaveTextContent('Searching...')
    expect(screen.getByTestId('search-button')).toBeDisabled()
  })

  it('should display search results after successful search', async () => {
    const mockOnSearch = vi.fn().mockResolvedValue(mockSearchResponse)
    
    const { rerender } = render(
      <SearchComponent 
        onSearch={mockOnSearch}
        loading={false}
        error={null}
        results={null}
      />
    )

    const searchButton = screen.getByTestId('search-button')
    await userEvent.click(searchButton)

    // Update to show results
    rerender(
      <SearchComponent 
        onSearch={mockOnSearch}
        loading={false}
        error={null}
        results={mockSearchResponse}
      />
    )

    expect(screen.getByTestId('search-results')).toBeInTheDocument()
    expect(screen.getByText('Found 1 flights and 1 hotels')).toBeInTheDocument()
  })

  it('should display error message when search fails', async () => {
    const mockError = new Error('Search failed')
    const mockOnSearch = vi.fn().mockRejectedValue(mockError)
    
    const { rerender } = render(
      <SearchComponent 
        onSearch={mockOnSearch}
        loading={false}
        error={null}
        results={null}
      />
    )

    const searchButton = screen.getByTestId('search-button')
    await userEvent.click(searchButton)

    // Update to show error
    rerender(
      <SearchComponent 
        onSearch={mockOnSearch}
        loading={false}
        error={mockError}
        results={null}
      />
    )

    expect(screen.getByTestId('error-message')).toBeInTheDocument()
    expect(screen.getByText('Search failed')).toBeInTheDocument()
  })

  it('should handle API mocking with MSW', async () => {
    // Setup mock handler
    server.use(
      http.post('http://localhost:8000/api/agent/search', () => {
        return HttpResponse.json(mockSearchResponse)
      })
    )

    // Mock the agentApiService.search method
    const originalSearch = agentApiService.search
    agentApiService.search = vi.fn().mockImplementation(async (params) => {
      const response = await fetch('http://localhost:8000/api/agent/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      })
      return response.json()
    })

    const { search } = useSearch()
    
    // Test the search function
    const searchParams = {
      origin: 'Beijing',
      destination: 'Tokyo',
      departure_date: '2025-02-01',
      passengers: 2
    }

    const result = await search(searchParams)
    
    expect(result).toEqual(mockSearchResponse)
    expect(agentApiService.search).toHaveBeenCalledWith(searchParams)

    // Restore original method
    agentApiService.search = originalSearch
  })

  it('should handle user input changes', async () => {
    const mockOnSearch = vi.fn()
    
    render(
      <SearchComponent 
        onSearch={mockOnSearch}
        loading={false}
        error={null}
        results={null}
      />
    )

    const originInput = screen.getByTestId('origin-input')
    const destinationInput = screen.getByTestId('destination-input')
    const passengersInput = screen.getByTestId('passengers-input')

    // Change input values
    await userEvent.clear(originInput)
    await userEvent.type(originInput, 'Shanghai')
    await userEvent.clear(destinationInput)
    await userEvent.type(destinationInput, 'Osaka')
    await userEvent.clear(passengersInput)
    await userEvent.type(passengersInput, '3')

    const searchButton = screen.getByTestId('search-button')
    await userEvent.click(searchButton)

    expect(mockOnSearch).toHaveBeenCalledWith({
      origin: 'Shanghai',
      destination: 'Osaka',
      departure_date: '2025-02-01',
      passengers: 3
    })
  })
})