# Interactively test the results of queries.
# This is a quick and dirty script...
# climb_bot could be much more modular to make this script easier to write and understand.

import re

from climb_bot import findmparea, findmproute

while True:
    query_string = input('Input a climb_bot command, or leave empty to exit: ')
    if query_string == '':
        break

    match = re.findall('(![Cc]limb|[Cc]limb:) (.*)', query_string)  # gives a list of tuples
    # (because there are two groups in the regex)

    if match:
        # logging.info('Found command ' + str(match) + ' in comment: ' + comment.id + ' ; ' + comment.permalink)
        query = match[0][1]  # take the first Tuple in the List, and the second regex group from the Tuple

        # if not check_already_commented(comment.id):
        if True:
            # logging.info('Comment ID has not been processed yet: ' + comment.id)
            # logging.debug('vars(comment): ' + str(vars(comment)))

            # check for  '!climb area' or 'climb: area'
            area_match = re.findall('[Aa]rea (.*)', query)
            if area_match:
                query = area_match[0]
                # logging.info('Found Area command in comment: ' + comment.id)
                # logging.debug('Searching MP for Area query: ' + query)
                current_area = findmparea(query)
                if current_area:
                    # logging.info('Posting reply to comment: ' + comment.id)
                    # comment.reply(current_area.redditstr() + config.bot_footer)
                    print(current_area.redditstr())
                    # logging.info('Reply posted to comment: ' + comment.id)
                    # record_comment(comment.id)
                else:
                    # logging.error('ERROR RETRIEVING AREA LINK AND INFO FROM MP. Comment: ' + comment.id +
                    #               '. Body: ' + comment.body)
                    print('Error retrieving area.')
            else:
                # check for Route command, otherwise assume we are handling a route.
                route_match = re.findall('[Rr]oute (.*)', query)
                if route_match:
                    query = route_match[0]
                    # logging.info('Found Route command in comment: ' + comment.id)
                else:
                    # logging.info('No additional command found; processing as Route command')
                    print('No additional command found; processing as Route command')

                # find the MP route link
                # logging.debug('Searching MP for Route query: ' + query)
                current_route = findmproute(query)
                if current_route:
                    # logging.info('Posting reply to comment: ' + comment.id)
                    # comment.reply(current_route.redditstr() + config.bot_footer)
                    print(current_route.redditstr())
                    # TODO does PRAW return the comment ID of the reply we just submitted? Log permalink
                    # logging.info('Reply posted to comment: ' + comment.id)
                    # record_comment(comment.id)
                else:
                    # logging.error('ERROR RETRIEVING ROUTE LINK AND INFO FROM MP. Comment: ' + comment.id +
                    #               '. Body: ' + comment.body)
                    print('Error retrieving route.')
