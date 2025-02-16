export default function Header() {
  return (
    <div>
      <header className="fixed top-0 left-0 w-full flex items-center justify-between border-b border-gray-200 px-10 py-3 bg-blue-500">
        {/* {Name} */}
        <h1 className="text-white text-2xl font-bold">HyperLang</h1>

        <label className="flex min-w-40 h-10 max-w-64">
          <div className="flex items-center bg-gray-100 rounded-xl px-4">
            <input
              type="text"
              placeholder="Search"
              className="ml-2 bg-gray-100 border-none outline-none text-black"
            />
          </div>
        </label>
      </header>

      <div className="flex flex-col items-center justify-center h-screen bg-gray-100 space-y-6">
        <div className="bg-black p-2 w-96 rounded-xl shadow-lg text-center">
          <h1 className="text-white">Scenarios</h1>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-lg w-96 text-center">
          <h2 className="text-2xl font-bold text-gray-800">
            Discuss your week
          </h2>
          <p className="text-gray-600 mt-2">
            Practice speaking about your week with a friend.
          </p>
          <button className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg">
            Start conversation
          </button>
        </div>
      </div>
    </div>
  );
}
