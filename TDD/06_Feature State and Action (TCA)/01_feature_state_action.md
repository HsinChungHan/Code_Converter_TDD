# Feature State and Action (TCA)

## LoadCodeWidget.Feature（擴展自 LoadBookingCodeSection.Feature）

### 復用策略

```swift
// 保持向後相容的方式：
// 1. State 新增屬性都有 default value
// 2. Action 新增 case 不影響既有邏輯
// 3. 可選擇性啟用 Code Converter 功能
```

---

### State（擴展）

```swift
@ObservableState
struct State: Equatable {
    // ========== 原有屬性（保持相容） ==========
    var bookingCode: String = ""
    var selectedCountry: Region = .current
    var isLoading: Bool = false
    var contentState: SectionContentState = .loaded
    var availableCountries: [Region] = [.ghana, .nigeria]
    
    // ========== 新增屬性（Code Converter） ==========
    
    /// 是否啟用 Code Converter 功能（向後相容開關）
    var enableCodeConverter: Bool = true
    
    /// 已選擇的 Bookie（包含 provider + country）
    var selectedBookie: SelectedBookie?
    
    /// Provider Config 列表（從 API 取得）
    var providerConfigs: [ProviderConfig] = []
    
    /// Widget 輸入狀態（6 種狀態）
    var inputState: WidgetInputState = .default
    
    /// Bookie 選擇器是否顯示
    var isBookieSelectorPresented: Bool = false
    
    /// 錯誤訊息
    var errorMessage: String?
    
    /// 轉換結果
    var convertResult: ConvertResult?
}
```

### State 屬性說明

| 屬性 | 類型 | 原有/新增 | 預設值 | 說明 |
|------|------|-----------|--------|------|
| `bookingCode` | String | ✅ 原有 | `""` | 輸入的 Booking Code |
| `selectedCountry` | Region | ✅ 原有 | `.current` | 選擇的國家 |
| `isLoading` | Bool | ✅ 原有 | `false` | Loading 狀態 |
| `contentState` | SectionContentState | ✅ 原有 | `.loaded` | Section 狀態 |
| `availableCountries` | [Region] | ✅ 原有 | `[.ghana, .nigeria]` | 可用國家 |
| `enableCodeConverter` | Bool | 🆕 新增 | `true` | 是否啟用 Code Converter |
| `selectedBookie` | SelectedBookie? | 🆕 新增 | `nil` | 已選 Bookie |
| `providerConfigs` | [ProviderConfig] | 🆕 新增 | `[]` | Provider 設定 |
| `inputState` | WidgetInputState | 🆕 新增 | `.default` | 6 種輸入狀態 |
| `isBookieSelectorPresented` | Bool | 🆕 新增 | `false` | Sheet 顯示 |
| `errorMessage` | String? | 🆕 新增 | `nil` | 錯誤訊息 |
| `convertResult` | ConvertResult? | 🆕 新增 | `nil` | 轉換結果 |

---

### Action（擴展）

```swift
@CasePathable
enum Action: Equatable {
    // ========== 原有 Action（保持相容） ==========
    case onAppear
    case bookingCodeChanged(String)
    case countrySelected(Region)
    case loadBookingCode
    case bookingCodeLoadFailed(String)
    case bookingCodeLoaded(LoadCodeModel.CodeResult)
    
    // ========== 新增 Action（Code Converter） ==========
    
    // UI Actions
    case bookieDropdownTapped
    case bookieSelectorDismissed
    case bookieSelected(provider: String, country: CountryCode)
    case inputFocused
    case inputBlurred
    case clearButtonTapped
    
    // Response Actions
    case providerConfigLoaded(Result<[ProviderConfig], Error>)
    case convertCodeCompleted(Result<ConvertBookingCodeOutput, Error>)
    
    // Navigation Actions
    case presentBetslip(shareCode: String, failCnt: Int)
}
```

### Action 對照表

| Action | 原有/新增 | 觸發時機 | 對應 UseCase |
|--------|-----------|----------|--------------|
| `.onAppear` | ✅ 原有 | 頁面出現 | - |
| `.bookingCodeChanged` | ✅ 原有 | 輸入變更 | - |
| `.countrySelected` | ✅ 原有 | 選擇國家（原流程） | - |
| `.loadBookingCode` | ✅ 原有 | 載入（原流程） | LoadCodeManager |
| `.bookingCodeLoadFailed` | ✅ 原有 | 載入失敗（原流程） | - |
| `.bookingCodeLoaded` | ✅ 原有 | 載入成功（原流程） | - |
| `.bookieDropdownTapped` | 🆕 新增 | 點擊 Bookie Dropdown | LoadProviderConfigUseCase |
| `.bookieSelectorDismissed` | 🆕 新增 | 關閉 Sheet | - |
| `.bookieSelected` | 🆕 新增 | 選擇 Bookie + Country | - |
| `.inputFocused` | 🆕 新增 | 輸入框聚焦 | - |
| `.inputBlurred` | 🆕 新增 | 輸入框失焦 | - |
| `.clearButtonTapped` | 🆕 新增 | 點擊清除按鈕 | - |
| `.providerConfigLoaded` | 🆕 新增 | Config 載入完成 | - |
| `.convertCodeCompleted` | 🆕 新增 | 轉換完成 | - |
| `.presentBetslip` | 🆕 新增 | 載入 Betslip | - |

---

### Reducer（擴展）

```swift
@Reducer
struct Feature: Reducer {
    typealias State = LoadCodeWidget.State
    typealias Action = LoadCodeWidget.Action
    
    @Dependency(\.currentRegion) var currentRegion
    @Dependency(\.loadProviderConfigUseCase) var loadProviderConfigUseCase
    @Dependency(\.convertBookingCodeUseCase) var convertBookingCodeUseCase
    
    private let manager: LoadCodeManager
    
    init(manager: LoadCodeManager = .init()) {
        self.manager = manager
    }
    
    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            // ========== 原有邏輯（保持不變） ==========
            case .onAppear:
                if state.availableCountries.contains(currentRegion) {
                    state.selectedCountry = currentRegion
                } else {
                    state.selectedCountry = state.availableCountries.first ?? .nigeria
                }
                // 新增：如果啟用 Code Converter，設置預設 Bookie
                if state.enableCodeConverter, let firstConfig = state.providerConfigs.first {
                    state.selectedBookie = SelectedBookie(from: firstConfig)
                }
                return .none
                
            case .bookingCodeChanged(let rawCode):
                let filteredCode = manager.filterBookingCode(rawCode)
                state.bookingCode = filteredCode
                // 新增：更新 inputState
                if state.enableCodeConverter {
                    state.inputState = filteredCode.isEmpty ? .focus : .typing
                    state.errorMessage = nil // 清除錯誤
                }
                return .none
                
            case .countrySelected(let country):
                state.selectedCountry = country
                return .none
                
            case .loadBookingCode:
                guard !state.bookingCode.isEmpty else {
                    return .run { send in
                        await send(.bookingCodeLoadFailed("Empty Code"))
                    }
                }
                
                // 新增：根據是否啟用 Code Converter 決定流程
                if state.enableCodeConverter, let bookie = state.selectedBookie {
                    // Code Converter 流程
                    state.inputState = .loading
                    state.isLoading = true
                    
                    let input = ConvertBookingCodeInput(
                        provider: bookie.provider,
                        country: bookie.country.rawValue,
                        bookingCode: state.bookingCode
                    )
                    return .run { send in
                        let result = await convertBookingCodeUseCase.execute(input)
                        await send(.convertCodeCompleted(result))
                    }
                } else {
                    // 原有流程
                    state.isLoading = true
                    state.contentState = .loaded
                    
                    return .run { [bookingCode = state.bookingCode, 
                                   country = state.selectedCountry] send in
                        do {
                            let result = try await manager.loadBookingCodeData(
                                shareCode: bookingCode, 
                                countryCode: country.apiCountryCode
                            )
                            await send(.bookingCodeLoaded(result))
                        } catch {
                            await send(.bookingCodeLoadFailed(manager.mapErrorToMessage(error)))
                        }
                    }
                }
                
            case .bookingCodeLoadFailed(let message):
                state.isLoading = false
                if state.enableCodeConverter {
                    state.inputState = .error(message: message)
                    state.errorMessage = message
                }
                return .none
                
            case .bookingCodeLoaded:
                state.isLoading = false
                state.bookingCode = ""
                if state.enableCodeConverter {
                    state.inputState = .default
                }
                return .none
                
            // ========== 新增邏輯（Code Converter） ==========
            case .bookieDropdownTapped:
                return .run { send in
                    let result = await loadProviderConfigUseCase.execute()
                    await send(.providerConfigLoaded(result))
                }
                
            case .bookieSelectorDismissed:
                state.isBookieSelectorPresented = false
                return .none
                
            case let .bookieSelected(provider, country):
                guard let config = state.providerConfigs.first(where: { $0.provider == provider }) else {
                    return .none
                }
                state.selectedBookie = SelectedBookie(
                    provider: provider,
                    name: config.name,
                    country: country
                )
                state.isBookieSelectorPresented = false
                // 同步更新 selectedCountry（向後相容）
                if let region = Region.from(countryCode: country) {
                    state.selectedCountry = region
                }
                return .none
                
            case .inputFocused:
                state.inputState = .focus
                return .none
                
            case .inputBlurred:
                if state.bookingCode.isEmpty {
                    state.inputState = .default
                } else {
                    state.inputState = .filled
                }
                return .none
                
            case .clearButtonTapped:
                state.bookingCode = ""
                state.inputState = .focus
                state.errorMessage = nil
                return .none
                
            case let .providerConfigLoaded(.success(configs)):
                state.providerConfigs = configs
                state.isBookieSelectorPresented = true
                // 同步更新 availableCountries（向後相容）
                state.availableCountries = configs.flatMap { $0.regions }
                return .none
                
            case let .providerConfigLoaded(.failure(error)):
                state.errorMessage = error.localizedDescription
                return .none
                
            case let .convertCodeCompleted(.success(output)):
                state.isLoading = false
                state.inputState = .filled
                state.convertResult = output.convertResult
                state.bookingCode = "" // 清空輸入
                return .send(.presentBetslip(
                    shareCode: output.convertResult.shareCode,
                    failCnt: output.convertResult.failCnt
                ))
                
            case let .convertCodeCompleted(.failure(error)):
                state.isLoading = false
                let message = (error as? CodeConverterError)?.localizedDescription ?? error.localizedDescription
                state.inputState = .error(message: message)
                state.errorMessage = message
                return .none
                
            case .presentBetslip:
                // 由外部處理 Betslip 導航
                return .none
            }
        }
    }
}
```

---

## Computed Properties

```swift
extension LoadCodeWidget.State {
    /// Load 按鈕是否啟用
    var isLoadButtonEnabled: Bool {
        guard !bookingCode.isEmpty else { return false }
        if enableCodeConverter {
            return selectedBookie != nil && inputState.isLoadButtonEnabled
        }
        return true
    }
    
    /// Dropdown 顯示文字
    var dropdownDisplayText: String {
        if enableCodeConverter, let bookie = selectedBookie {
            return bookie.displayText
        }
        return selectedCountry.description
    }
    
    /// 是否顯示清除按鈕
    var showClearButton: Bool {
        !bookingCode.isEmpty && (inputState == .typing || inputState == .filled || inputState.isError)
    }
    
    /// Loading 提示文字
    var loadingHintText: String? {
        guard inputState == .loading else { return nil }
        return "Conversion may take up to 10 seconds, please stay here and wait for the result."
    }
}
```
