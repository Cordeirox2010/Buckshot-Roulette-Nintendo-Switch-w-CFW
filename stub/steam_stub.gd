extends Node
# Stub of the GodotSteam singleton ("Steam") so Buckshot Roulette can run on Linux arm64,
# where Steamworks does not exist. It does no networking: it only satisfies the script parser
# and returns neutral values. Registered as the autoload "Steam" via override.cfg (see installer.py).

# --- signals used by the game (never emitted) ---
signal persona_state_change
signal p2p_session_request
signal p2p_session_connect_fail
signal lobby_match_list
signal lobby_joined
signal lobby_created
signal lobby_chat_update
signal leaderboard_scores_downloaded
signal leaderboard_score_uploaded
signal leaderboard_find_result
signal join_requested
signal avatar_loaded

# --- constants ---
const LOBBY_TYPE_FRIENDS_ONLY = 1
const LOBBY_TYPE_PUBLIC = 2
const LOBBY_DISTANCE_FILTER_CLOSE = 1
const LOBBY_DISTANCE_FILTER_FAR = 2
const LOBBY_DISTANCE_FILTER_WORLDWIDE = 3
const LEADERBOARD_DATA_REQUEST_GLOBAL = 0
const LEADERBOARD_DATA_REQUEST_GLOBAL_AROUND_USER = 1
const LEADERBOARD_DATA_REQUEST_FRIENDS = 2
const P2P_SEND_RELIABLE = 2
const CHAT_ROOM_ENTER_RESPONSE_SUCCESS = 1
const CHAT_ROOM_ENTER_RESPONSE_DOESNT_EXIST = 2
const CHAT_ROOM_ENTER_RESPONSE_NOT_ALLOWED = 3
const CHAT_ROOM_ENTER_RESPONSE_FULL = 4
const CHAT_ROOM_ENTER_RESPONSE_ERROR = 5
const CHAT_ROOM_ENTER_RESPONSE_BANNED = 6
const CHAT_ROOM_ENTER_RESPONSE_LIMITED = 7
const CHAT_ROOM_ENTER_RESPONSE_CLAN_DISABLED = 8
const CHAT_ROOM_ENTER_RESPONSE_COMMUNITY_BAN = 9
const CHAT_ROOM_ENTER_RESPONSE_MEMBER_BLOCKED_YOU = 10
const CHAT_ROOM_ENTER_RESPONSE_YOU_BLOCKED_MEMBER = 11
const CHAT_MEMBER_STATE_CHANGE_ENTERED = 1
const CHAT_MEMBER_STATE_CHANGE_LEFT = 2
const CHAT_MEMBER_STATE_CHANGE_KICKED = 8
const CHAT_MEMBER_STATE_CHANGE_BANNED = 16

# --- methods (optional arguments so the analyzer accepts any arity) ---
func steamInit(p1 = null, p2 = null, p3 = null):
	return {"status": 1, "verbal": "Steam disabled (arm64 stub)"}

func run_callbacks():
	pass

func loggedOn():
	return false

func getSteamID():
	return 0

func getPersonaName():
	return "Player"

func getFriendPersonaName(p1 = null):
	return "Player"

func isSteamRunningOnSteamDeck():
	return false

func getPlayerAvatar(p1 = null, p2 = null, p3 = null):
	return null

func setAchievement(p1 = null):
	return true

func clearAchievement(p1 = null):
	return true

func storeStats():
	return true

# lobbies / multiplayer (disabled)
func createLobby(p1 = null, p2 = null, p3 = null):
	pass

func joinLobby(p1 = null):
	pass

func leaveLobby(p1 = null):
	pass

func requestLobbyList():
	pass

func getLobbyData(p1 = null, p2 = null):
	return ""

func setLobbyData(p1 = null, p2 = null, p3 = null):
	return false

func setLobbyJoinable(p1 = null, p2 = null):
	return false

func setLobbyType(p1 = null, p2 = null):
	return false

func setLobbyMemberLimit(p1 = null, p2 = null):
	return false

func getLobbyOwner(p1 = null):
	return 0

func getNumLobbyMembers(p1 = null):
	return 0

func getLobbyMemberByIndex(p1 = null, p2 = null):
	return 0

func addRequestLobbyListDistanceFilter(p1 = null):
	pass

func addRequestLobbyListResultCountFilter(p1 = null):
	pass

func activateGameOverlayInviteDialog(p1 = null):
	pass

# P2P (disabled)
func sendP2PPacket(p1 = null, p2 = null, p3 = null, p4 = null, p5 = null):
	return false

func readP2PPacket(p1 = null, p2 = null, p3 = null):
	return {}

func getAvailableP2PPacketSize(p1 = null):
	return 0

func acceptP2PSessionWithUser(p1 = null):
	pass

func closeP2PSessionWithUser(p1 = null):
	return false

func allowP2PPacketRelay(p1 = null):
	return false

# leaderboards (disabled)
func findLeaderboard(p1 = null):
	pass

func downloadLeaderboardEntries(p1 = null, p2 = null, p3 = null, p4 = null, p5 = null):
	pass

func uploadLeaderboardScore(p1 = null, p2 = null, p3 = null, p4 = null, p5 = null, p6 = null):
	pass

func setLeaderboardDetailsMax(p1 = null):
	return false

func getLeaderboardEntryCount(p1 = null):
	return 0
