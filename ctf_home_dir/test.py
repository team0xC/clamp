import swpag_client
team = swpag_client.Team('http://52.37.204.0/', 'nt4yw7LjoPFc2WE49cLG')

s = 'FLGHVVksOwTWXjSc2a5t5i0p0hFLGinNClUb9Y0b4g6c1x1c7e2lFLGe8vjnBPTw5LpD1c0x0h6f1eFLGNQ4MI2FldvP8S0k6j9f8t3lFLGMPO9HhWgUUPHgFLG6HX2HV86stV0TFLGrSH0Zy8adEwgk6v5r1z7m5aFLGaPZICPIz98HpK2f4g4c0m9fFLGl6aMn3D8DPqDrFLGIhoLBCxWq6gEjFLGfJeZS86QKKU9W7e9o0n5e2nFLGZoWsJbKQQuKnP7m9w3o2k6dFLGAaX1tMyoCXdbt4t9i0f7m8nFLGXzz6Vdi9A0hSMFLG4Lgh0beUNBF950o5s9h8q4rFLGXieZWrSa7DbYvFLGc2WNZY623S1gH4u3t8e6q4iFLGRicpKfjAkO6dQ1k6y8z1k7hFLG4eFlnrKbJLpWkFLGs05dbMgN1gqwi1b8o3k4q9vFLGABBiznQDdz0Ul5a0x2e3p9vFLGJSRmwopJCyGk93v7a3a9u8aFLG0hg0JSTuoiovHFLGdwoY3wS7JceoaFLG6krqnR68QpOUp4o9i1l5v3cFLG9wlqDgYI1utpEFLGhc1yd5A9Vu7P63z4e8t5d0nFLGiHpybzm07EIcF6o5g1s9z4nFLGxsIm7kT37BaJt0q1e5x3i5hFLGt0tF3uqtS3LFCFLGxzipAy3Me593mFLGZBUiOvOByLCcb6k7x4f7i7uFLGjeW4EE9SrNY610j4p9o3h9yFLGd38P7qQHFveZF4m4o2g9z3tFLGgLg0EUwebh4ZW4u4c1g1r6bFLG2B2fcPpGrjCmD2g9z4j9s1gFLGTCvVtjNHNkvjc7z7i1g2z0a'
flags = []
for f in s.split('FLG'):
  if len(f) > 0:
    flags.append('FLG' + f)

print(flags)

batches = (len(flags) // 100) + 1
for i in range(batches):
  batch = flags[i*100:(i+1)*100]
  if len(batch) > 0:
    results = team.submit_flag(flags)
  count = 0
  for result in results:
    if result == u'correct':
      count += 1
  print(str(count) + " correct!\n")